"""
Behavioral Profile Model
Stores user behavioral biometric data for authentication
"""

from datetime import datetime
from app.firebase_config import db

class BehavioralProfile:
    """Model for storing user behavioral biometric profiles"""
    
    COLLECTION_NAME = 'behavioral_profiles'
    
    def __init__(self, user_id, keystroke_patterns=None, mouse_patterns=None, 
                 navigation_patterns=None, time_patterns=None, baseline_established=False,
                 baseline_data_points=0, last_updated=None, created_at=None):
        self.user_id = user_id
        self.keystroke_patterns = keystroke_patterns or {}
        self.mouse_patterns = mouse_patterns or {}
        self.navigation_patterns = navigation_patterns or {}
        self.time_patterns = time_patterns or {}
        self.baseline_established = baseline_established
        self.baseline_data_points = baseline_data_points
        self.last_updated = last_updated or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'user_id': self.user_id,
            'keystroke_patterns': self.keystroke_patterns,
            'mouse_patterns': self.mouse_patterns,
            'navigation_patterns': self.navigation_patterns,
            'time_patterns': self.time_patterns,
            'baseline_established': self.baseline_established,
            'baseline_data_points': self.baseline_data_points,
            'last_updated': self.last_updated,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create model from dictionary"""
        return BehavioralProfile(
            user_id=data.get('user_id'),
            keystroke_patterns=data.get('keystroke_patterns', {}),
            mouse_patterns=data.get('mouse_patterns', {}),
            navigation_patterns=data.get('navigation_patterns', {}),
            time_patterns=data.get('time_patterns', {}),
            baseline_established=data.get('baseline_established', False),
            baseline_data_points=data.get('baseline_data_points', 0),
            last_updated=data.get('last_updated'),
            created_at=data.get('created_at')
        )
    
    def save(self):
        """Save behavioral profile to Firestore"""
        try:
            doc_ref = db.collection(self.COLLECTION_NAME).document(self.user_id)
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving behavioral profile: {e}")
            return False
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get behavioral profile by user ID"""
        try:
            doc_ref = db.collection(BehavioralProfile.COLLECTION_NAME).document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return BehavioralProfile.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting behavioral profile: {e}")
            return None
    
    @staticmethod
    def create_or_update(user_id, keystroke_patterns=None, mouse_patterns=None,
                        navigation_patterns=None, time_patterns=None):
        """Create or update behavioral profile"""
        try:
            existing_profile = BehavioralProfile.get_by_user_id(user_id)
            
            if existing_profile:
                # Update existing profile
                if keystroke_patterns:
                    existing_profile.keystroke_patterns = keystroke_patterns
                if mouse_patterns:
                    existing_profile.mouse_patterns = mouse_patterns
                if navigation_patterns:
                    existing_profile.navigation_patterns = navigation_patterns
                if time_patterns:
                    existing_profile.time_patterns = time_patterns
                
                existing_profile.last_updated = datetime.utcnow()
                existing_profile.baseline_data_points += 1
                
                # Establish baseline after 2 weeks (assuming daily sessions)
                if existing_profile.baseline_data_points >= 14:
                    existing_profile.baseline_established = True
                
                existing_profile.save()
                return existing_profile
            else:
                # Create new profile
                profile = BehavioralProfile(
                    user_id=user_id,
                    keystroke_patterns=keystroke_patterns or {},
                    mouse_patterns=mouse_patterns or {},
                    navigation_patterns=navigation_patterns or {},
                    time_patterns=time_patterns or {},
                    baseline_data_points=1
                )
                profile.save()
                return profile
        except Exception as e:
            print(f"Error creating/updating behavioral profile: {e}")
            return None
    
    def update_patterns(self, keystroke_patterns=None, mouse_patterns=None,
                       navigation_patterns=None, time_patterns=None):
        """Update behavioral patterns"""
        if keystroke_patterns:
            self.keystroke_patterns = keystroke_patterns
        if mouse_patterns:
            self.mouse_patterns = mouse_patterns
        if navigation_patterns:
            self.navigation_patterns = navigation_patterns
        if time_patterns:
            self.time_patterns = time_patterns
        
        self.last_updated = datetime.utcnow()
        self.baseline_data_points += 1
        
        # Establish baseline after collecting enough data
        if self.baseline_data_points >= 14:
            self.baseline_established = True
        
        return self.save()
