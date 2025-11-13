"""Device Profile Model"""
from datetime import datetime
from app.firebase_config import db

class DeviceProfile:
    COLLECTION_NAME = 'device_profiles'
    
    def __init__(self, device_id=None, user_id=None, device_name=None, os_version=None,
                 os_updated=False, has_antivirus=False, antivirus_updated=False,
                 is_encrypted=False, is_known=False, is_compliant=True,
                 trust_score=70, last_seen=None, created_at=None):
        self.device_id = device_id
        self.user_id = user_id
        self.device_name = device_name
        self.os_version = os_version
        self.os_updated = os_updated
        self.has_antivirus = has_antivirus
        self.antivirus_updated = antivirus_updated
        self.is_encrypted = is_encrypted
        self.is_known = is_known
        self.is_compliant = is_compliant
        self.trust_score = trust_score
        self.last_seen = last_seen or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            'device_id': self.device_id,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'os_version': self.os_version,
            'os_updated': self.os_updated,
            'has_antivirus': self.has_antivirus,
            'antivirus_updated': self.antivirus_updated,
            'is_encrypted': self.is_encrypted,
            'is_known': self.is_known,
            'is_compliant': self.is_compliant,
            'trust_score': self.trust_score,
            'last_seen': self.last_seen,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        return DeviceProfile(**data)
    
    def save(self):
        try:
            doc_ref = db.collection(DeviceProfile.COLLECTION_NAME).document(self.device_id)
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving device profile: {e}")
            return False
    
    @staticmethod
    def get_by_device_id(device_id):
        try:
            doc_ref = db.collection(DeviceProfile.COLLECTION_NAME).document(device_id)
            doc = doc_ref.get()
            return DeviceProfile.from_dict(doc.to_dict()) if doc.exists else None
        except:
            return None
