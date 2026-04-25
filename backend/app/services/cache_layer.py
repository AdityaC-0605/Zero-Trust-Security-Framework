import time
from typing import Optional, Any, Callable
from firebase_admin import firestore
import threading

class CacheLayer:
    def __init__(self):
        self._cache = {}
        self.db = firestore.client()
        self.lock = threading.Lock()

    def get(self, key: str, fallback_fn: Callable[[], Any], ttl_seconds: int = 60) -> Any:
        now = time.time()
        
        with self.lock:
            if key in self._cache:
                entry = self._cache[key]
                if now - entry["timestamp"] < entry["ttl"]:
                    return entry["value"]
                else:
                    del self._cache[key]
        
        # Cache miss or expired
        val = fallback_fn()
            
        with self.lock:
            self._cache[key] = {
                "value": val,
                "timestamp": time.time(),
                "ttl": ttl_seconds
            }
        return val

    def invalidate(self, key: str):
        with self.lock:
            if key in self._cache:
                del self._cache[key]

# Global instance
cache_layer = CacheLayer()
