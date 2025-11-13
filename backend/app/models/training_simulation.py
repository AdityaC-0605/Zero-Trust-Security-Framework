"""Training Simulation Models"""
from datetime import datetime
from app.firebase_config import db

class SecuritySimulation:
    COLLECTION_NAME = 'security_simulations'
    
    def __init__(self, simulation_id=None, title=None, sim_type=None, difficulty=None,
                 scenario=None, steps=None, correct_actions=None, points=10):
        self.simulation_id = simulation_id
        self.title = title
        self.sim_type = sim_type
        self.difficulty = difficulty
        self.scenario = scenario
        self.steps = steps or []
        self.correct_actions = correct_actions or []
        self.points = points
    
    def to_dict(self):
        return {
            'simulation_id': self.simulation_id,
            'title': self.title,
            'type': self.sim_type,
            'difficulty': self.difficulty,
            'scenario': self.scenario,
            'steps': self.steps,
            'correct_actions': self.correct_actions,
            'points': self.points
        }
    
    def save(self):
        try:
            if not self.simulation_id:
                doc_ref = db.collection(self.COLLECTION_NAME).document()
                self.simulation_id = doc_ref.id
            else:
                doc_ref = db.collection(self.COLLECTION_NAME).document(self.simulation_id)
            doc_ref.set(self.to_dict())
            return True
        except:
            return False

class UserTrainingProgress:
    COLLECTION_NAME = 'user_training_progress'
    
    def __init__(self, user_id=None, completed_simulations=None, security_awareness_score=0,
                 badges=None, last_training=None):
        self.user_id = user_id
        self.completed_simulations = completed_simulations or []
        self.security_awareness_score = security_awareness_score
        self.badges = badges or []
        self.last_training = last_training
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'completed_simulations': self.completed_simulations,
            'security_awareness_score': self.security_awareness_score,
            'badges': self.badges,
            'last_training': self.last_training
        }
    
    def save(self):
        try:
            doc_ref = db.collection(self.COLLECTION_NAME).document(self.user_id)
            doc_ref.set(self.to_dict())
            return True
        except:
            return False
    
    @staticmethod
    def get_by_user_id(user_id):
        try:
            doc_ref = db.collection(UserTrainingProgress.COLLECTION_NAME).document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return UserTrainingProgress(**data)
            return UserTrainingProgress(user_id=user_id)
        except:
            return UserTrainingProgress(user_id=user_id)
