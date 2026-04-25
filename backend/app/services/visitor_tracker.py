import math
import datetime
from typing import Dict, Any, List, Optional
from firebase_admin import firestore

class VisitorTrackerService:
    def __init__(self):
        self.deviation_threshold_meters = 50.0

    def get_db(self):
        return firestore.client()

    def haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371000.0 # radius in meters
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def compute_compliance_score(self, current_waypoints: int, total_assigned: int) -> float:
        if total_assigned <= 0:
            return 1.0
        score = current_waypoints / float(total_assigned)
        return max(0.0, min(score, 1.0))

    def _emit_websocket_alert(self, visitor_id: str, alert_type: str, message: str):
        # Placeholder for websocket emitting logic
        pass

    def check_deviation(self, visitor_id: str, current_lat: float, current_lon: float, route_points: List[Dict[str, float]]) -> bool:
        if not route_points:
            return False
            
        distances = [self.haversine(current_lat, current_lon, pt.get("lat", 0), pt.get("lon", 0)) for pt in route_points]
        min_dist = min(distances)
        
        if min_dist > self.deviation_threshold_meters:
            self._emit_websocket_alert(visitor_id, "Route_Compliance", f"Deviation by {min_dist:.1f}m")
            return True
        return False

    def predict_zone_entry(self, visitor_id: str, location_history: List[Dict[str, Any]], restricted_zones: List[Dict[str, Any]]) -> bool:
        if len(location_history) < 2:
            return False

        p1 = location_history[-2]
        p2 = location_history[-1]
        
        t1 = p1.get("timestamp")
        t2 = p2.get("timestamp")
        
        if isinstance(t1, str): t1 = datetime.datetime.fromisoformat(t1.replace('Z', '+00:00'))
        if isinstance(t2, str): t2 = datetime.datetime.fromisoformat(t2.replace('Z', '+00:00'))
        
        seconds = (t2 - t1).total_seconds()
        if seconds <= 0:
            return False
            
        lat_velocity = (p2["lat"] - p1["lat"]) / seconds
        lon_velocity = (p2["lon"] - p1["lon"]) / seconds
        
        proj_lat = p2["lat"] + lat_velocity * 60.0
        proj_lon = p2["lon"] + lon_velocity * 60.0
        
        for zone in restricted_zones:
            dist = self.haversine(proj_lat, proj_lon, zone.get("lat", 0), zone.get("lon", 0))
            if dist <= zone.get("radius_meters", 10.0):
                self._emit_websocket_alert(visitor_id, "Predictive_Zone_Entry", f"Projected to enter zone {zone.get('id')} within 60s")
                return True
        return False

    def ingest_location(self, visitor_id: str, location_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        db = self.get_db()
        visitor_ref = db.collection("visitors").document(visitor_id)
        doc = visitor_ref.get()
        
        if not doc.exists:
            return None
            
        data = doc.to_dict() or {}
        source = location_data.get("source", "gps")
        
        current_lat = location_data.get("lat", 0.0)
        current_lon = location_data.get("lon", 0.0)
        
        route_points = data.get("assigned_route", [])
        
        self.check_deviation(visitor_id, current_lat, current_lon, route_points)
        
        total_assigned = len(route_points)
        waypoints_reached = data.get("waypoints_reached", 0)
        compliance_score = self.compute_compliance_score(waypoints_reached, total_assigned)
        
        current_time = datetime.datetime.now(datetime.timezone.utc)
        new_loc = {
            "lat": current_lat,
            "lon": current_lon,
            "source": source,
            "timestamp": current_time.isoformat(),
            "compliance_score": compliance_score
        }
        
        session_id = data.get("current_session_id")
        if session_id:
            db.collection("visitors").document(visitor_id).collection("active_session").add(new_loc)
            hist = list(db.collection("visitors").document(visitor_id).collection("active_session")
                        .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(2).stream())
            hist_dicts = [h.to_dict() for h in reversed(hist)]
            restricted_zones = data.get("restricted_zones", [])
            self.predict_zone_entry(visitor_id, hist_dicts, restricted_zones)
            
        visitor_ref.update({
            "current_lat": current_lat,
            "current_lon": current_lon,
            "compliance_score": compliance_score,
            "last_location_update": current_time.isoformat()
        })
        
        return {"compliance_score": compliance_score}

    def terminate_session(self, visitor_id: str) -> bool:
        db = self.get_db()
        visitor_ref = db.collection("visitors").document(visitor_id)
        
        doc = visitor_ref.get()
        if not doc.exists:
            return False
            
        active_session = db.collection("visitors").document(visitor_id).collection("active_session")
        docs = active_session.stream()
        
        history = []
        for d in docs:
            history.append(d.to_dict())
            d.reference.delete()
            
        if history:
            db.collection("visitors").document(visitor_id).collection("location_history").add({
                "session_end": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "history": history
            })
            
        visitor_ref.update({
            "current_session_id": None,
            "compliance_score": 0.0
        })
        return True
