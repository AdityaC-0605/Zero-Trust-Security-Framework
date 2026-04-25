from firebase_admin import firestore
import datetime

class AuthPolicyEnforcer:
    def __init__(self):
        self.db = firestore.client()

    def validate_password(self, password: str) -> bool:
        return len(password) >= 12

    def track_failed_attempt(self, user_id: str) -> bool:
        """Returns True if user is now locked out, False otherwise"""
        ref = self.db.collection("auth_attempts").document(user_id)
        doc = ref.get()
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if doc.exists:
            data = doc.to_dict()
            first_fail = data.get("first_failure")
            count = data.get("count", 0)
            
            if isinstance(first_fail, str):
                first_fail = datetime.datetime.fromisoformat(first_fail)
                
            if (now - first_fail).total_seconds() < 900: # 15 minutes
                count += 1
            else:
                count = 1
                first_fail = now
                
            ref.set({
                "count": count,
                "first_failure": first_fail.isoformat(),
                "locked": count >= 5
            })
            return count >= 5
        else:
            ref.set({
                "count": 1,
                "first_failure": now.isoformat(),
                "locked": False
            })
            return False

    def is_locked(self, user_id: str) -> bool:
        doc = self.db.collection("auth_attempts").document(user_id).get()
        if doc.exists:
            return doc.to_dict().get("locked", False)
        return False

auth_policy_enforcer = AuthPolicyEnforcer()
