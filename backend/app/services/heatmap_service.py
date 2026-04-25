import datetime
import threading
import time
from typing import Dict, List, Any
from firebase_admin import firestore

class HeatmapService:
    def __init__(self):
        self.db = firestore.client()
        self.push_interval = 5.0
        self._stop_event = threading.Event()
        self._thread = None
        self.subscribers = set()
    
    def start_push_loop(self):
        if not self._thread:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop_push_loop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None

    def _loop(self):
        while not self._stop_event.is_set():
            data = self.aggregate_layers()
            self._push_to_subscribers(data)
            time.sleep(self.push_interval)

    def register_subscriber(self, callback):
        self.subscribers.add(callback)

    def remove_subscriber(self, callback):
        self.subscribers.discard(callback)

    def _push_to_subscribers(self, data):
        for cb in self.subscribers:
            try:
                cb(data)
            except Exception:
                pass

    def aggregate_layers(self) -> Dict[str, Any]:
        return {
            "active_users": self._get_active_users_layer(),
            "visitors": self._get_visitors_layer(),
            "failed_auth": self._get_failed_auth_layer(),
            "threats": self._get_threats_layer(),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    def _get_active_users_layer(self):
        return [{"zone_id": "zoneA", "location": [37.7749, -122.4194], "intensity": 0.8}]
        
    def _get_visitors_layer(self):
        return [{"zone_id": "zoneB", "location": [37.7750, -122.4180], "intensity": 0.5}]
        
    def _get_failed_auth_layer(self):
        return [{"zone_id": "zoneA", "location": [37.7749, -122.4194], "intensity": 0.2}]
        
    def _get_threats_layer(self):
        return [{"zone_id": "zoneC", "location": [37.7730, -122.4170], "intensity": 0.9}]

    def get_zone_events(self, zone_id: str) -> List[Dict[str, Any]]:
        return [
            {"event_id": "ev1", "type": "auth_failure", "zone_id": zone_id, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()},
            {"event_id": "ev2", "type": "threat_alert", "zone_id": zone_id, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        ]
