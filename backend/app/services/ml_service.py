import datetime
import math
from typing import Dict, Any, List
from firebase_admin import firestore

class MLService:
    def __init__(self):
        self.db = firestore.client()
        self.current_f1 = 0.85

    def _log_inference(self, endpoint: str, inputs: Dict[str, Any], raw_output: Dict[str, Any]):
        try:
            self.db.collection("ml_inferences").add({
                "endpoint": endpoint,
                "inputs": inputs,
                "outputs": raw_output,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
        except Exception:
            pass

    def emit_high_threat_alert(self, probability: float, features: Dict[str, Any]):
        try:
            self.db.collection("alerts").add({
                "type": "high_threat",
                "threat_probability": probability,
                "features": features,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
        except Exception:
            pass

    def classify_intent(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        if "delete" in lower or "rm -rf" in lower:
            label = "destructive"
            conf = 0.95
        elif "reboot" in lower:
            label = "maintenance"
            conf = 0.88
        else:
            label = "benign"
            conf = 0.99
            
        res = {"label": label, "confidence": max(0.0, min(1.0, conf))}
        self._log_inference("intent", {"text": text}, res)
        return res

    def predict_threat(self, features: Dict[str, Any]) -> Dict[str, float]:
        base_threat = 0.1
        trust = features.get("trust_score", 1.0)
        sensitivity = features.get("resource_sensitivity", 0.0)
        failed = features.get("recent_failed_attempts", 0)
        
        prob = base_threat + (1.0 - trust) * 0.4 + (sensitivity) * 0.3 + (failed * 0.1)
        prob = max(0.0, min(1.0, prob))
        
        if prob > 0.75:
            self.emit_high_threat_alert(prob, features)
            
        res = {"threat_probability": float(prob)}
        self._log_inference("threat", features, res)
        return res

    def detect_anomaly(self, request_features: List[float]) -> Dict[str, Any]:
        if not request_features:
            return {"is_anomaly": False, "anomaly_score": 0.0}
            
        avg_val = sum(request_features) / len(request_features)
        score = 1.0 / (1.0 + math.exp(-avg_val + 2.0))
        
        score = max(0.0, min(1.0, score))        
        res = {"is_anomaly": score > 0.7, "anomaly_score": score}
        self._log_inference("anomaly", {"vector": request_features}, res)
        return res

    def deploy_new_model(self, model_name: str, test_f1: float) -> bool:
        if test_f1 > self.current_f1:
            self.current_f1 = test_f1
            try:
                self.db.collection("ml_models").add({
                    "model_name": model_name,
                    "f1_score": test_f1,
                    "deployment_time": datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
            except Exception:
                pass
            return True
        return False
