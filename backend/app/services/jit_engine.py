import datetime
from typing import Dict, Any, Tuple
from firebase_admin import firestore
from app.services.cache_layer import cache_layer

class JITEngineService:
    def __init__(self):
        self._weights = {
            "identity": 0.3,
            "device_trust": 0.25,
            "behavioral_ctx": 0.25,
            "policy_compliance": 0.20
        }
        self.last_weight_update = datetime.datetime.now(datetime.timezone.utc)
        self.db = firestore.client()

    def reload_weights(self):
        def _fetch():
            doc = self.db.collection("config").document("jit_weights").get()
            return doc.to_dict() if doc.exists else {}
            
        data = cache_layer.get("jit_weights", _fetch, ttl_seconds=60)
        
        if data:
            self._weights["identity"] = data.get("identity", 0.3)
            self._weights["device_trust"] = data.get("device_trust", 0.25)
            self._weights["behavioral_ctx"] = data.get("behavioral_ctx", 0.25)
            self._weights["policy_compliance"] = data.get("policy_compliance", 0.20)
            self.last_weight_update = datetime.datetime.now(datetime.timezone.utc)

    def compute_confidence(self, identity: float, device_trust: float, behavioral_ctx: float, policy_compliance: float, ml_adjustment: float = 0.0) -> float:
        ml_adj = max(-0.1, min(0.1, ml_adjustment))
        
        score = (identity * self._weights["identity"] +
                 device_trust * self._weights["device_trust"] +
                 behavioral_ctx * self._weights["behavioral_ctx"] +
                 policy_compliance * self._weights["policy_compliance"])
                 
        return score + ml_adj

    def process_request(self, req_id: str, identity: float, device_trust: float, behavioral_ctx: float, policy_compliance: float, ml_adjustment: float = 0.0) -> str:
        score = self.compute_confidence(identity, device_trust, behavioral_ctx, policy_compliance, ml_adjustment)
        
        if score >= 0.8:
            decision = "auto-grant"
        elif score >= 0.5:
            decision = "route-to-admin"
        else:
            decision = "auto-deny"
            
        self.db.collection("jit_requests").document(req_id).set({
            "identity": identity,
            "device_trust": device_trust,
            "behavioral_ctx": behavioral_ctx,
            "policy_compliance": policy_compliance,
            "ml_adjustment": ml_adjustment,
            "confidence_score": score,
            "decision": decision,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        return decision

    def auto_revoke_expired(self):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        docs = self.db.collection("jit_grants").where("status", "==", "active").where("expires_at", "<=", now).stream()
        for doc in docs:
            doc.reference.update({"status": "revoked", "revoked_at": now})
            self.db.collection("audit_logs").add({
                "action": "jit_auto_revoke",
                "grant_id": doc.id,
                "timestamp": now
            })
