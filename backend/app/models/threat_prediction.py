"""
Threat Prediction Model
Stores predicted security threats
"""

from datetime import datetime
from app.firebase_config import db


class ThreatPrediction:
    """Model for storing threat predictions"""
    
    COLLECTION_NAME = 'threat_predictions'
    
    def __init__(self, prediction_id=None, user_id=None, threat_type=None,
                 confidence=None, threat_score=None, indicators=None,
                 preventive_measures=None, predicted_at=None, status='pending',
                 outcome=None, outcome_timestamp=None, admin_notified=False):
        self.prediction_id = prediction_id
        self.user_id = user_id
        self.threat_type = threat_type
        self.confidence = confidence
        self.threat_score = threat_score
        self.indicators = indicators or []
        self.preventive_measures = preventive_measures or []
        self.predicted_at = predicted_at or datetime.utcnow()
        self.status = status  # pending, confirmed, false_positive, prevented
        self.outcome = outcome
        self.outcome_timestamp = outcome_timestamp
        self.admin_notified = admin_notified
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'prediction_id': self.prediction_id,
            'user_id': self.user_id,
            'threat_type': self.threat_type,
            'confidence': self.confidence,
            'threat_score': self.threat_score,
            'indicators': self.indicators,
            'preventive_measures': self.preventive_measures,
            'predicted_at': self.predicted_at,
            'status': self.status,
            'outcome': self.outcome,
            'outcome_timestamp': self.outcome_timestamp,
            'admin_notified': self.admin_notified
        }
    
    @staticmethod
    def from_dict(data):
        """Create model from dictionary"""
        return ThreatPrediction(
            prediction_id=data.get('prediction_id'),
            user_id=data.get('user_id'),
            threat_type=data.get('threat_type'),
            confidence=data.get('confidence'),
            threat_score=data.get('threat_score'),
            indicators=data.get('indicators', []),
            preventive_measures=data.get('preventive_measures', []),
            predicted_at=data.get('predicted_at'),
            status=data.get('status', 'pending'),
            outcome=data.get('outcome'),
            outcome_timestamp=data.get('outcome_timestamp'),
            admin_notified=data.get('admin_notified', False)
        )
    
    def save(self):
        """Save threat prediction to Firestore"""
        try:
            if not self.prediction_id:
                doc_ref = db.collection(self.COLLECTION_NAME).document()
                self.prediction_id = doc_ref.id
            else:
                doc_ref = db.collection(self.COLLECTION_NAME).document(self.prediction_id)
            
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving threat prediction: {e}")
            return False
    
    @staticmethod
    def get_by_id(prediction_id):
        """Get threat prediction by ID"""
        try:
            doc_ref = db.collection(ThreatPrediction.COLLECTION_NAME).document(prediction_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return ThreatPrediction.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting threat prediction: {e}")
            return None
    
    @staticmethod
    def get_by_user_id(user_id, limit=10):
        """Get threat predictions for a user"""
        try:
            query = db.collection(ThreatPrediction.COLLECTION_NAME)\
                     .where('user_id', '==', user_id)\
                     .order_by('predicted_at', direction='DESCENDING')\
                     .limit(limit)
            
            docs = query.stream()
            predictions = []
            
            for doc in docs:
                predictions.append(ThreatPrediction.from_dict(doc.to_dict()))
            
            return predictions
        except Exception as e:
            print(f"Error getting user threat predictions: {e}")
            return []
    
    @staticmethod
    def get_pending_predictions(limit=50):
        """Get pending threat predictions"""
        try:
            query = db.collection(ThreatPrediction.COLLECTION_NAME)\
                     .where('status', '==', 'pending')\
                     .order_by('confidence', direction='DESCENDING')\
                     .limit(limit)
            
            docs = query.stream()
            predictions = []
            
            for doc in docs:
                predictions.append(ThreatPrediction.from_dict(doc.to_dict()))
            
            return predictions
        except Exception as e:
            print(f"Error getting pending predictions: {e}")
            return []
    
    @staticmethod
    def get_high_confidence_predictions(confidence_threshold=0.80, limit=20):
        """Get high confidence threat predictions"""
        try:
            query = db.collection(ThreatPrediction.COLLECTION_NAME)\
                     .where('confidence', '>=', confidence_threshold)\
                     .where('status', '==', 'pending')\
                     .order_by('confidence', direction='DESCENDING')\
                     .limit(limit)
            
            docs = query.stream()
            predictions = []
            
            for doc in docs:
                predictions.append(ThreatPrediction.from_dict(doc.to_dict()))
            
            return predictions
        except Exception as e:
            print(f"Error getting high confidence predictions: {e}")
            return []
    
    def update_outcome(self, outcome, outcome_timestamp=None):
        """Update prediction outcome"""
        self.outcome = outcome
        self.outcome_timestamp = outcome_timestamp or datetime.utcnow()
        
        # Update status based on outcome
        if outcome == 'confirmed':
            self.status = 'confirmed'
        elif outcome == 'false_positive':
            self.status = 'false_positive'
        elif outcome == 'prevented':
            self.status = 'prevented'
        
        return self.save()
    
    def mark_admin_notified(self):
        """Mark that admin has been notified"""
        self.admin_notified = True
        return self.save()


class ThreatIndicator:
    """Model for storing individual threat indicators"""
    
    COLLECTION_NAME = 'threat_indicators'
    
    def __init__(self, indicator_id=None, user_id=None, indicator_type=None,
                 severity=None, value=None, description=None, detected_at=None,
                 resolved=False, resolved_at=None):
        self.indicator_id = indicator_id
        self.user_id = user_id
        self.indicator_type = indicator_type
        self.severity = severity
        self.value = value
        self.description = description
        self.detected_at = detected_at or datetime.utcnow()
        self.resolved = resolved
        self.resolved_at = resolved_at
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'indicator_id': self.indicator_id,
            'user_id': self.user_id,
            'indicator_type': self.indicator_type,
            'severity': self.severity,
            'value': self.value,
            'description': self.description,
            'detected_at': self.detected_at,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create model from dictionary"""
        return ThreatIndicator(
            indicator_id=data.get('indicator_id'),
            user_id=data.get('user_id'),
            indicator_type=data.get('indicator_type'),
            severity=data.get('severity'),
            value=data.get('value'),
            description=data.get('description'),
            detected_at=data.get('detected_at'),
            resolved=data.get('resolved', False),
            resolved_at=data.get('resolved_at')
        )
    
    def save(self):
        """Save threat indicator to Firestore"""
        try:
            if not self.indicator_id:
                doc_ref = db.collection(self.COLLECTION_NAME).document()
                self.indicator_id = doc_ref.id
            else:
                doc_ref = db.collection(self.COLLECTION_NAME).document(self.indicator_id)
            
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving threat indicator: {e}")
            return False
    
    @staticmethod
    def get_active_indicators(user_id=None, limit=50):
        """Get active (unresolved) threat indicators"""
        try:
            query = db.collection(ThreatIndicator.COLLECTION_NAME)\
                     .where('resolved', '==', False)
            
            if user_id:
                query = query.where('user_id', '==', user_id)
            
            query = query.order_by('detected_at', direction='DESCENDING').limit(limit)
            
            docs = query.stream()
            indicators = []
            
            for doc in docs:
                indicators.append(ThreatIndicator.from_dict(doc.to_dict()))
            
            return indicators
        except Exception as e:
            print(f"Error getting active indicators: {e}")
            return []
    
    def resolve(self):
        """Mark indicator as resolved"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        return self.save()
