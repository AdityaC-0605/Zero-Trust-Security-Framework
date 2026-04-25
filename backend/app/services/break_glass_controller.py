import hashlib
import json
import datetime
from io import BytesIO
from typing import Dict, Any, List
from firebase_admin import firestore

try:
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None

class BreakGlassController:
    def __init__(self):
        self.db = firestore.client()
        self.mismatch_threshold = 0.8

    def _emit_websocket_alert(self, message: str):
        pass

    def request_access(self, user_id: str, level: int, justification: str) -> Dict[str, Any]:
        req_id = "bg_" + str(hash(user_id + justification + str(datetime.datetime.now())))
        
        status = "pending"
        
        if level == 3:
            self._emit_websocket_alert(f"Level 3 Break-Glass requested by {user_id}: {justification}")
            
        self.db.collection("break_glass_requests").document(req_id).set({
            "user_id": user_id,
            "level": level,
            "justification": justification,
            "status": status,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        return {"request_id": req_id, "status": status}

    def approve_request(self, req_id: str, approver_id: str, approver_role: str) -> bool:
        doc = self.db.collection("break_glass_requests").document(req_id).get()
        if not doc.exists:
            return False
            
        data = doc.to_dict()
        level = data.get("level", 1)
        
        if level == 3 and approver_role != "senior_admin":
            return False 
            
        doc.reference.update({
            "status": "approved",
            "approver_id": approver_id,
            "approved_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        return True

    def compute_sha256(self, entries: List[Dict[str, Any]]) -> str:
        stringified = json.dumps(entries, sort_keys=True)
        return hashlib.sha256(stringified.encode('utf-8')).hexdigest()

    def record_session_action(self, req_id: str, action: str):
        coll = self.db.collection("break_glass_requests").document(req_id).collection("session_records")
        entry = {
            "action": action,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        coll.add(entry)
        
        docs = coll.order_by("timestamp").stream()
        all_entries = [d.to_dict() for d in docs]
        
        current_hash = self.compute_sha256(all_entries)
        self.db.collection("break_glass_requests").document(req_id).update({
            "session_checksum": current_hash
        })
        
        doc = self.db.collection("break_glass_requests").document(req_id).get()
        justification = doc.to_dict().get("justification", "")
        
        mismatch_score = self._analyze_mismatch(justification, action)
        if mismatch_score > self.mismatch_threshold:
            self._emit_websocket_alert(f"Suspicious activity in session {req_id}: {action}")

    def _analyze_mismatch(self, justification: str, action: str) -> float:
        if "delete" in action.lower() and "read" in justification.lower():
            return 0.9
        return 0.1

    def generate_report(self, req_id: str) -> bytes:
        doc = self.db.collection("break_glass_requests").document(req_id).get()
        data = doc.to_dict() if doc.exists else {}
        
        buffer = BytesIO()
        if canvas:
            c = canvas.Canvas(buffer)
            c.drawString(100, 800, f"Post-Incident Report: {req_id}")
            c.drawString(100, 780, f"User: {data.get('user_id')}")
            c.drawString(100, 760, f"Justification: {data.get('justification')}")
            c.showPage()
            c.save()
        else:
            buffer.write(b"PDF Generation skipped (reportlab not available)")
            
        return buffer.getvalue()
