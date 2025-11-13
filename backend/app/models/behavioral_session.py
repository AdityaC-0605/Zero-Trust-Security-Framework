"""
Behavioral Session Model
Stores session-level behavioral data for real-time analysis
"""

from datetime import datetime
from app.firebase_config import db

class BehavioralSession:
    """Model for storing session-level behavioral data"""
    
    COLLECTION_NAME = 'behavioral_sessions'
    
    def __init__(self, session_id, user_id, keystroke_data=None, mouse_data=None,
                 click_data=None, scroll_data=None, navigation_data=None,
                 metadata=None, risk_score=None, anomalies=None,
                 session_start=None, last_activity=None):
        self.session_id = session_id
        self.user_id = user_id
        self.keystroke_data = keystroke_data or []
        self.mouse_data = mouse_data or []
        self.click_data = click_data or []
        self.scroll_data = scroll_data or []
        self.navigation_data = navigation_data or []
        self.metadata = metadata or {}
        self.risk_score = risk_score
        self.anomalies = anomalies or []
        self.session_start = session_start or datetime.utcnow()
        self.last_activity = last_activity or datetime.utcnow()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'keystroke_data': self.keystroke_data,
            'mouse_data': self.mouse_data,
            'click_data': self.click_data,
            'scroll_data': self.scroll_data,
            'navigation_data': self.navigation_data,
            'metadata': self.metadata,
            'risk_score': self.risk_score,
            'anomalies': self.anomalies,
            'session_start': self.session_start,
            'last_activity': self.last_activity
        }
    
    @staticmethod
    def from_dict(data):
        """Create model from dictionary"""
        return BehavioralSession(
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            keystroke_data=data.get('keystroke_data', []),
            mouse_data=data.get('mouse_data', []),
            click_data=data.get('click_data', []),
            scroll_data=data.get('scroll_data', []),
            navigation_data=data.get('navigation_data', []),
            metadata=data.get('metadata', {}),
            risk_score=data.get('risk_score'),
            anomalies=data.get('anomalies', []),
            session_start=data.get('session_start'),
            last_activity=data.get('last_activity')
        )
    
    def save(self):
        """Save behavioral session to Firestore"""
        try:
            doc_ref = db.collection(self.COLLECTION_NAME).document(str(self.session_id))
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving behavioral session: {e}")
            return False
    
    @staticmethod
    def get_by_session_id(session_id):
        """Get behavioral session by session ID"""
        try:
            doc_ref = db.collection(BehavioralSession.COLLECTION_NAME).document(str(session_id))
            doc = doc_ref.get()
            
            if doc.exists:
                return BehavioralSession.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting behavioral session: {e}")
            return None
    
    @staticmethod
    def get_by_user_id(user_id, limit=10):
        """Get recent behavioral sessions for a user"""
        try:
            query = db.collection(BehavioralSession.COLLECTION_NAME)\
                     .where('user_id', '==', user_id)\
                     .order_by('session_start', direction='DESCENDING')\
                     .limit(limit)
            
            docs = query.stream()
            sessions = []
            
            for doc in docs:
                sessions.append(BehavioralSession.from_dict(doc.to_dict()))
            
            return sessions
        except Exception as e:
            print(f"Error getting user behavioral sessions: {e}")
            return []
    
    def append_behavioral_data(self, keystroke_data=None, mouse_data=None,
                              click_data=None, scroll_data=None, navigation_data=None):
        """Append new behavioral data to session"""
        if keystroke_data:
            self.keystroke_data.extend(keystroke_data)
        if mouse_data:
            self.mouse_data.extend(mouse_data)
        if click_data:
            self.click_data.extend(click_data)
        if scroll_data:
            self.scroll_data.extend(scroll_data)
        if navigation_data:
            self.navigation_data.extend(navigation_data)
        
        self.last_activity = datetime.utcnow()
        return self.save()
    
    def update_risk_score(self, risk_score, anomalies=None):
        """Update session risk score"""
        self.risk_score = risk_score
        if anomalies:
            self.anomalies.extend(anomalies)
        self.last_activity = datetime.utcnow()
        return self.save()
    
    @staticmethod
    def create_session(session_id, user_id, keystroke_data=None, mouse_data=None,
                      click_data=None, scroll_data=None, navigation_data=None, metadata=None):
        """Create a new behavioral session"""
        try:
            session = BehavioralSession(
                session_id=session_id,
                user_id=user_id,
                keystroke_data=keystroke_data or [],
                mouse_data=mouse_data or [],
                click_data=click_data or [],
                scroll_data=scroll_data or [],
                navigation_data=navigation_data or [],
                metadata=metadata or {}
            )
            session.save()
            return session
        except Exception as e:
            print(f"Error creating behavioral session: {e}")
            return None
    
    def get_session_duration(self):
        """Get session duration in seconds"""
        if self.session_start and self.last_activity:
            delta = self.last_activity - self.session_start
            return delta.total_seconds()
        return 0
    
    def get_activity_count(self):
        """Get total activity count"""
        return (len(self.keystroke_data) + len(self.mouse_data) + 
                len(self.click_data) + len(self.scroll_data) + 
                len(self.navigation_data))
