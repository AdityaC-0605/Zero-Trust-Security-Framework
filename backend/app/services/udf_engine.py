import math
import datetime
from typing import Dict, List, Any, Optional

from firebase_admin import firestore

class UDFEngine:
    """
    Unclonable Device Fingerprinting (UDF) Engine
    Responsible for fingerprint ingestion, Trust_Score computation, anomaly detection.
    """
    
    def __init__(self):
        self.jaccard_weights = {
            "hardware": 0.3,
            "browser": 0.3,
            "network": 0.2,
            "behavioral": 0.2
        }
        self.time_decay_lambda = math.log(10) / 30.0

    def get_db(self):
        return firestore.client()

    def _jaccard_index(self, set_a: set, set_b: set) -> float:
        if not set_a and not set_b:
            return 1.0 # Both empty -> 1.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / union if union > 0 else 0.0

    def compute_weighted_jaccard(self, current_fp: Dict[str, Any], baseline_fp: Dict[str, Any]) -> float:
        score = 0.0
        for category, weight in self.jaccard_weights.items():
            set_a = set(current_fp.get(category, []))
            set_b = set(baseline_fp.get(category, []))
            score += weight * self._jaccard_index(set_a, set_b)
        return score

    def time_decay(self, days_since_observation: float) -> float:
        return math.exp(-self.time_decay_lambda * days_since_observation)

    def parse_timestamp(self, ts_input: Any) -> datetime.datetime:
        if isinstance(ts_input, datetime.datetime):
            return ts_input
        elif isinstance(ts_input, str):
            return datetime.datetime.fromisoformat(ts_input.replace('Z', '+00:00'))
        else:
            return datetime.datetime.now(datetime.timezone.utc)

    def compute_trust_score(self, current_fp: Dict[str, Any], baseline_fp: Dict[str, Any], history: List[Dict[str, Any]], current_time: Optional[datetime.datetime] = None) -> float:
        if current_time is None:
            current_time = datetime.datetime.now(datetime.timezone.utc)
            
        current_jaccard = self.compute_weighted_jaccard(current_fp, baseline_fp)
        
        # Current observation
        total_score = self.time_decay(0) * current_jaccard
        total_weight = self.time_decay(0)

        for obs in history:
            obs_time = self.parse_timestamp(obs.get("timestamp"))
            delta = current_time - obs_time
            days_since = delta.total_seconds() / 86400.0
            if days_since < 0:
                days_since = 0

            decay_weight = self.time_decay(days_since)
            obs_jaccard = obs.get("weighted_jaccard", 0.0)
            
            total_score += decay_weight * obs_jaccard
            total_weight += decay_weight

        trust_score = total_score / total_weight if total_weight > 0 else 0.0

        # Apply bounds
        trust_score = max(0.0, min(trust_score, 1.0))

        # Caps for VM/automation
        if current_fp.get("vm_detected", False) or current_fp.get("automation_detected", False):
            trust_score = min(trust_score, 0.4)

        return trust_score

    def detect_impossible_travel(self, session_a: Dict[str, Any], session_b: Dict[str, Any]) -> bool:
        """
        session_x: contains 'lat', 'lon', 'timestamp'
        Returns True if required speed > 900 km/h
        """
        lat1 = session_a.get("lat")
        lon1 = session_a.get("lon")
        lat2 = session_b.get("lat")
        lon2 = session_b.get("lon")
        
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return False

        t1 = self.parse_timestamp(session_a.get("timestamp"))
        t2 = self.parse_timestamp(session_b.get("timestamp"))

        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        hours = abs((t2 - t1).total_seconds()) / 3600.0
        if hours == 0:
            return distance > 0 # Any distance in 0 hours is impossible travel

        speed = distance / hours
        return speed > 900.0

    def detect_characteristic_drift(self, history_7d: List[Dict[str, Any]]) -> bool:
        if not history_7d or len(history_7d) < 2:
            return False
            
        first_jaccard = history_7d[0].get("weighted_jaccard", 1.0)
        last_jaccard = history_7d[-1].get("weighted_jaccard", 1.0)
        
        delta = abs(first_jaccard - last_jaccard)
        return delta > 0.20

    def process_device(self, device_id: str, user_id: str, current_fp: Dict[str, Any], current_session: Dict[str, Any], last_session: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete processing flow for a device fingerprint based on requirements.
        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        db = self.get_db()
        device_ref = db.collection("devices").document(device_id)
        doc = device_ref.get()
        
        if doc.exists:
            device_data = doc.to_dict()
            baseline_fp = device_data.get("baseline_fingerprint", {})
            history = device_data.get("history", [])
        else:
            baseline_fp = current_fp
            history = []
            
        impossible_travel = False
        if last_session and current_session:
            impossible_travel = self.detect_impossible_travel(last_session, current_session)
            
        current_jaccard = self.compute_weighted_jaccard(current_fp, baseline_fp)
        trust_score = self.compute_trust_score(current_fp, baseline_fp, history, current_time)
        
        if impossible_travel:
            trust_score = min(trust_score, 0.3)
            
        # Get 7-day history to detect drift
        history_7d = [h for h in history if (current_time - self.parse_timestamp(h.get("timestamp"))).total_seconds() / 86400.0 <= 7]
        history_7d_with_current = history_7d + [{"weighted_jaccard": current_jaccard}]
        drift_detected = self.detect_characteristic_drift(history_7d_with_current)
        
        new_entry = {
            "timestamp": current_time.isoformat(),
            "weighted_jaccard": current_jaccard,
            "trust_score": trust_score,
            "score": trust_score
        }
        history.append(new_entry)
        
        # Retain history for 90 days
        retained_history = [h for h in history if (current_time - self.parse_timestamp(h.get("timestamp"))).total_seconds() / 86400.0 <= 90]
        
        update_data = {
            "device_id": device_id,
            "user_id": user_id,
            "trust_score_history": retained_history,
            "history": retained_history,
            "vm_detected": current_fp.get("vm_detected", False),
            "automation_detected": current_fp.get("automation_detected", False),
            "last_seen": current_time.isoformat(),
            "baseline_fingerprint": baseline_fp
        }
        
        if not doc.exists:
            update_data["created_at"] = current_time.isoformat()
            
        device_ref.set(update_data, merge=True)
        
        return {
            "trust_score": trust_score,
            "impossible_travel": impossible_travel,
            "drift_detected": drift_detected,
            "vm_detected": current_fp.get("vm_detected", False),
            "automation_detected": current_fp.get("automation_detected", False)
        }
