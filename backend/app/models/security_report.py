"""Security Report Models"""
from datetime import datetime
import uuid
from app.firebase_config import db


class SecurityReport:
    """Security Report model for user-submitted security concerns"""
    
    COLLECTION_NAME = 'securityReports'
    
    # Valid report types
    VALID_REPORT_TYPES = [
        'suspicious_access',
        'phishing',
        'social_engineering',
        'policy_violation',
        'data_breach',
        'unauthorized_access',
        'other'
    ]
    
    # Valid severity levels
    VALID_SEVERITY = ['low', 'medium', 'high', 'critical']
    
    # Valid status values
    VALID_STATUS = ['pending', 'verified', 'false_positive', 'resolved']
    
    def __init__(
        self,
        report_id=None,
        reported_by=None,
        report_type=None,
        target_user_id=None,
        target_resource=None,
        description=None,
        severity='medium',
        status='pending',
        verified_by=None,
        timestamp=None,
        resolution=None,
        evidence_urls=None,
        related_incidents=None
    ):
        """
        Initialize SecurityReport model
        
        Args:
            report_id (str): Unique report identifier
            reported_by (str): User ID of reporter
            report_type (str): Type of security report
            target_user_id (str): User ID being reported (if applicable)
            target_resource (str): Resource being reported
            description (str): Detailed description of the security concern
            severity (str): Severity level (low, medium, high, critical)
            status (str): Report status (pending, verified, false_positive, resolved)
            verified_by (str): Admin user ID who verified the report
            timestamp (datetime): When report was submitted
            resolution (str): Resolution notes
            evidence_urls (list): URLs to screenshots or evidence
            related_incidents (list): Related incident IDs
        """
        self.report_id = report_id or str(uuid.uuid4())
        self.reported_by = reported_by
        self.report_type = report_type
        self.target_user_id = target_user_id
        self.target_resource = target_resource
        self.description = description
        self.severity = severity
        self.status = status
        self.verified_by = verified_by
        self.timestamp = timestamp or datetime.utcnow()
        self.resolution = resolution
        self.evidence_urls = evidence_urls or []
        self.related_incidents = related_incidents or []
    
    def to_dict(self):
        """Convert SecurityReport to dictionary for Firestore"""
        return {
            'reportId': self.report_id,
            'reportedBy': self.reported_by,
            'reportType': self.report_type,
            'targetUserId': self.target_user_id,
            'targetResource': self.target_resource,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'verifiedBy': self.verified_by,
            'timestamp': self.timestamp,
            'resolution': self.resolution,
            'evidenceUrls': self.evidence_urls,
            'relatedIncidents': self.related_incidents
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create SecurityReport from dictionary"""
        return cls(
            report_id=data.get('reportId'),
            reported_by=data.get('reportedBy'),
            report_type=data.get('reportType'),
            target_user_id=data.get('targetUserId'),
            target_resource=data.get('targetResource'),
            description=data.get('description'),
            severity=data.get('severity', 'medium'),
            status=data.get('status', 'pending'),
            verified_by=data.get('verifiedBy'),
            timestamp=data.get('timestamp'),
            resolution=data.get('resolution'),
            evidence_urls=data.get('evidenceUrls', []),
            related_incidents=data.get('relatedIncidents', [])
        )
    
    def validate(self):
        """Validate security report data"""
        if not self.reported_by:
            return False, "Reporter user ID is required"
        
        if not self.report_type:
            return False, "Report type is required"
        
        if self.report_type not in self.VALID_REPORT_TYPES:
            return False, f"Report type must be one of: {', '.join(self.VALID_REPORT_TYPES)}"
        
        if not self.description:
            return False, "Description is required"
        
        if self.severity not in self.VALID_SEVERITY:
            return False, f"Severity must be one of: {', '.join(self.VALID_SEVERITY)}"
        
        if self.status not in self.VALID_STATUS:
            return False, f"Status must be one of: {', '.join(self.VALID_STATUS)}"
        
        return True, None
    
    def save(self):
        """Save security report to Firestore"""
        try:
            is_valid, error_message = self.validate()
            if not is_valid:
                raise Exception(f"Validation failed: {error_message}")
            
            doc_ref = db.collection(self.COLLECTION_NAME).document(self.report_id)
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving security report: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, report_id):
        """Get security report by ID"""
        try:
            doc = db.collection(cls.COLLECTION_NAME).document(report_id).get()
            if doc.exists:
                return cls.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting security report: {e}")
            return None
    
    @classmethod
    def get_all(cls, filters=None, limit=100):
        """Get all security reports with optional filters"""
        try:
            query = db.collection(cls.COLLECTION_NAME)
            
            if filters:
                if 'status' in filters:
                    query = query.where('status', '==', filters['status'])
                if 'severity' in filters:
                    query = query.where('severity', '==', filters['severity'])
                if 'reportedBy' in filters:
                    query = query.where('reportedBy', '==', filters['reportedBy'])
            
            query = query.order_by('timestamp', direction='DESCENDING').limit(limit)
            
            reports = []
            for doc in query.stream():
                reports.append(cls.from_dict(doc.to_dict()))
            
            return reports
        except Exception as e:
            print(f"Error getting security reports: {e}")
            return []


class UserSecurityReputation:
    """User Security Reputation model for tracking security contributions"""
    
    COLLECTION_NAME = 'userSecurityReputation'
    
    # Badge thresholds
    BADGE_THRESHOLDS = {
        'security_novice': 10,
        'security_contributor': 25,
        'security_guardian': 50
    }
    
    # Rank thresholds
    RANK_THRESHOLDS = [
        (0, 'novice'),
        (50, 'contributor'),
        (100, 'guardian'),
        (200, 'sentinel'),
        (500, 'champion')
    ]
    
    def __init__(
        self,
        user_id=None,
        reports_submitted=0,
        verified_reports=0,
        false_positives=0,
        reputation_score=0,
        badges=None,
        points=0,
        rank='novice',
        contribution_history=None
    ):
        """
        Initialize UserSecurityReputation model
        
        Args:
            user_id (str): User ID
            reports_submitted (int): Total reports submitted
            verified_reports (int): Number of verified reports
            false_positives (int): Number of false positive reports
            reputation_score (int): Overall reputation score (0-100)
            badges (list): List of earned badges
            points (int): Total points earned
            rank (str): User rank
            contribution_history (list): History of contributions
        """
        self.user_id = user_id
        self.reports_submitted = reports_submitted
        self.verified_reports = verified_reports
        self.false_positives = false_positives
        self.reputation_score = reputation_score
        self.badges = badges or []
        self.points = points
        self.rank = rank
        self.contribution_history = contribution_history or []
    
    def to_dict(self):
        """Convert UserSecurityReputation to dictionary"""
        return {
            'userId': self.user_id,
            'reportsSubmitted': self.reports_submitted,
            'verifiedReports': self.verified_reports,
            'falsePositives': self.false_positives,
            'reputationScore': self.reputation_score,
            'badges': self.badges,
            'points': self.points,
            'rank': self.rank,
            'contributionHistory': self.contribution_history
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create UserSecurityReputation from dictionary"""
        return cls(
            user_id=data.get('userId'),
            reports_submitted=data.get('reportsSubmitted', 0),
            verified_reports=data.get('verifiedReports', 0),
            false_positives=data.get('falsePositives', 0),
            reputation_score=data.get('reputationScore', 0),
            badges=data.get('badges', []),
            points=data.get('points', 0),
            rank=data.get('rank', 'novice'),
            contribution_history=data.get('contributionHistory', [])
        )
    
    def calculate_reputation_score(self):
        """Calculate reputation score based on verified reports and false positives"""
        if self.reports_submitted == 0:
            return 0
        
        accuracy = (self.verified_reports / self.reports_submitted) * 100
        penalty = (self.false_positives / self.reports_submitted) * 50
        
        score = max(0, min(100, accuracy - penalty))
        self.reputation_score = int(score)
        return self.reputation_score
    
    def update_rank(self):
        """Update user rank based on points"""
        for threshold, rank_name in reversed(self.RANK_THRESHOLDS):
            if self.points >= threshold:
                self.rank = rank_name
                break
    
    def check_and_award_badges(self):
        """Check if user has earned new badges"""
        new_badges = []
        
        for badge_name, threshold in self.BADGE_THRESHOLDS.items():
            if self.verified_reports >= threshold:
                badge_data = {
                    'badgeId': badge_name,
                    'name': badge_name.replace('_', ' ').title(),
                    'earnedAt': datetime.utcnow(),
                    'icon': f'/badges/{badge_name}.png'
                }
                
                # Check if badge already exists
                if not any(b.get('badgeId') == badge_name for b in self.badges):
                    self.badges.append(badge_data)
                    new_badges.append(badge_data)
        
        return new_badges
    
    def add_contribution(self, action, points_earned):
        """Add contribution to history"""
        contribution = {
            'timestamp': datetime.utcnow(),
            'action': action,
            'pointsEarned': points_earned
        }
        self.contribution_history.append(contribution)
        self.points += points_earned
        self.update_rank()
    
    def save(self):
        """Save user reputation to Firestore"""
        try:
            doc_ref = db.collection(self.COLLECTION_NAME).document(self.user_id)
            doc_ref.set(self.to_dict())
            return True
        except Exception as e:
            print(f"Error saving user reputation: {e}")
            return False
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get user reputation by user ID"""
        try:
            doc = db.collection(cls.COLLECTION_NAME).document(user_id).get()
            if doc.exists:
                return cls.from_dict(doc.to_dict())
            else:
                # Create new reputation record
                reputation = cls(user_id=user_id)
                reputation.save()
                return reputation
        except Exception as e:
            print(f"Error getting user reputation: {e}")
            return None
    
    @classmethod
    def get_leaderboard(cls, limit=100):
        """Get security leaderboard"""
        try:
            query = db.collection(cls.COLLECTION_NAME).order_by('points', direction='DESCENDING').limit(limit)
            
            leaderboard = []
            for doc in query.stream():
                leaderboard.append(cls.from_dict(doc.to_dict()))
            
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
