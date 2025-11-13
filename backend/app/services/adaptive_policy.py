"""Adaptive Policy Engine - Tracks and optimizes policies"""
import os
from datetime import datetime, timedelta
from app.firebase_config import db

class AdaptivePolicyEngine:
    def __init__(self):
        self.enabled = os.getenv('ADAPTIVE_POLICY_ENABLED', 'false').lower() == 'true'
        self.effectiveness_threshold = float(os.getenv('POLICY_EFFECTIVENESS_THRESHOLD', '70'))
    
    def track_policy_outcome(self, policy_id, request_id, outcome, correct):
        """Track policy decision outcome"""
        try:
            doc_ref = db.collection('policy_outcomes').document()
            doc_ref.set({
                'policy_id': policy_id,
                'request_id': request_id,
                'outcome': outcome,
                'correct': correct,
                'timestamp': datetime.utcnow()
            })
            return True
        except:
            return False
    
    def calculate_effectiveness(self, policy_id, days=7):
        """Calculate policy effectiveness score"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = db.collection('policy_outcomes')\
                     .where('policy_id', '==', policy_id)\
                     .where('timestamp', '>=', cutoff)
            
            docs = query.stream()
            total = 0
            correct = 0
            
            for doc in docs:
                data = doc.to_dict()
                total += 1
                if data.get('correct'):
                    correct += 1
            
            return (correct / total * 100) if total > 0 else 70
        except:
            return 70
    
    def generate_recommendations(self, policy_id):
        """Generate policy optimization recommendations"""
        effectiveness = self.calculate_effectiveness(policy_id)
        recommendations = []
        
        if effectiveness < 70:
            recommendations.append({
                'type': 'adjust_threshold',
                'action': 'decrease',
                'amount': 5,
                'reason': f'Low effectiveness: {effectiveness}%'
            })
        elif effectiveness > 95:
            recommendations.append({
                'type': 'adjust_threshold',
                'action': 'increase',
                'amount': 5,
                'reason': f'High effectiveness: {effectiveness}%, can relax'
            })
        
        return recommendations
    
    def auto_adjust_policy(self, policy_id):
        """Automatically adjust policy based on effectiveness"""
        if not self.enabled:
            return False
        
        recommendations = self.generate_recommendations(policy_id)
        
        for rec in recommendations:
            # Log the adjustment
            db.collection('policy_evolution').document().set({
                'policy_id': policy_id,
                'change_type': rec['type'],
                'action': rec['action'],
                'amount': rec['amount'],
                'reason': rec['reason'],
                'timestamp': datetime.utcnow()
            })
        
        return True

adaptive_policy = AdaptivePolicyEngine()
