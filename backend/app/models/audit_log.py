"""
Audit Log Model
Defines the AuditLog data structure and validation for Firestore
"""

from datetime import datetime
import uuid


class AuditLog:
    """Audit Log model for tracking system events"""
    
    # Valid event types
    VALID_EVENT_TYPES = [
        'access_request',
        'authentication',
        'admin_action',
        'policy_change',
        'mfa_event',
        'system_error'
    ]
    
    # Valid result types
    VALID_RESULTS = ['success', 'failure', 'denied']
    
    # Valid severity levels
    VALID_SEVERITY = ['low', 'medium', 'high', 'critical']
    
    def __init__(
        self,
        event_type,
        user_id,
        action,
        resource,
        result,
        ip_address=None,
        severity='low',
        log_id=None
    ):
        """
        Initialize AuditLog model
        
        Args:
            event_type (str): Type of event (access_request, authentication, etc.)
            user_id (str): User ID associated with the event
            action (str): Specific action description
            resource (str): Affected resource
            result (str): Result of the action (success, failure, denied)
            ip_address (str, optional): Client IP address
            severity (str): Severity level (low, medium, high, critical)
            log_id (str, optional): Log ID (auto-generated if not provided)
        """
        self.log_id = log_id or str(uuid.uuid4())
        self.event_type = event_type
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.result = result
        self.details = {}
        self.timestamp = datetime.utcnow()
        self.ip_address = ip_address
        self.severity = severity
    
    def to_dict(self):
        """
        Convert AuditLog object to dictionary for Firestore storage
        
        Returns:
            dict: Audit log data as dictionary
        """
        return {
            'logId': self.log_id,
            'eventType': self.event_type,
            'userId': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'result': self.result,
            'details': self.details,
            'timestamp': self.timestamp,
            'ipAddress': self.ip_address,
            'severity': self.severity
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create AuditLog object from dictionary
        
        Args:
            data (dict): Audit log data dictionary
            
        Returns:
            AuditLog: AuditLog object
        """
        log = cls(
            event_type=data.get('eventType'),
            user_id=data.get('userId'),
            action=data.get('action'),
            resource=data.get('resource'),
            result=data.get('result'),
            ip_address=data.get('ipAddress'),
            severity=data.get('severity', 'low'),
            log_id=data.get('logId')
        )
        
        log.details = data.get('details', {})
        log.timestamp = data.get('timestamp', datetime.utcnow())
        
        return log
    
    def validate(self):
        """
        Validate audit log data
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate required fields
        if not self.event_type:
            return False, "Event type is required"
        
        if not self.user_id:
            return False, "User ID is required"
        
        if not self.action:
            return False, "Action is required"
        
        if not self.resource:
            return False, "Resource is required"
        
        if not self.result:
            return False, "Result is required"
        
        # Validate event type
        if self.event_type not in self.VALID_EVENT_TYPES:
            return False, f"Event type must be one of: {', '.join(self.VALID_EVENT_TYPES)}"
        
        # Validate result
        if self.result not in self.VALID_RESULTS:
            return False, f"Result must be one of: {', '.join(self.VALID_RESULTS)}"
        
        # Validate severity
        if self.severity not in self.VALID_SEVERITY:
            return False, f"Severity must be one of: {', '.join(self.VALID_SEVERITY)}"
        
        return True, None
    
    def set_details(self, details):
        """
        Set additional details for the audit log
        
        Args:
            details (dict): Additional context and information
        """
        self.details = details


def create_audit_log(
    db,
    event_type,
    user_id,
    action,
    resource,
    result,
    details=None,
    ip_address=None,
    severity='low'
):
    """
    Create a new audit log document in Firestore
    
    Args:
        db: Firestore client
        event_type (str): Type of event
        user_id (str): User ID
        action (str): Action description
        resource (str): Affected resource
        result (str): Result of action
        details (dict, optional): Additional details
        ip_address (str, optional): Client IP address
        severity (str): Severity level
        
    Returns:
        AuditLog: Created audit log object
        
    Raises:
        Exception: If validation fails or creation fails
    """
    # Create audit log object
    audit_log = AuditLog(
        event_type=event_type,
        user_id=user_id,
        action=action,
        resource=resource,
        result=result,
        ip_address=ip_address,
        severity=severity
    )
    
    # Set details if provided
    if details:
        audit_log.set_details(details)
    
    # Validate audit log data
    is_valid, error_message = audit_log.validate()
    if not is_valid:
        raise Exception(f"Audit log validation failed: {error_message}")
    
    # Create audit log document in Firestore
    log_ref = db.collection('auditLogs').document(audit_log.log_id)
    log_ref.set(audit_log.to_dict())
    
    return audit_log


def get_audit_logs(db, filters=None, limit=100):
    """
    Get audit logs from Firestore with optional filtering
    
    Args:
        db: Firestore client
        filters (dict, optional): Filter criteria
        limit (int): Maximum number of logs to return
        
    Returns:
        list: List of AuditLog objects
    """
    logs_ref = db.collection('auditLogs')
    query = logs_ref
    
    # Apply filters if provided
    if filters:
        if 'userId' in filters:
            query = query.where('userId', '==', filters['userId'])
        
        if 'eventType' in filters:
            query = query.where('eventType', '==', filters['eventType'])
        
        if 'severity' in filters:
            query = query.where('severity', '==', filters['severity'])
        
        if 'result' in filters:
            query = query.where('result', '==', filters['result'])
    
    # Order by timestamp descending
    query = query.order_by('timestamp', direction='DESCENDING').limit(limit)
    
    logs = []
    for doc in query.stream():
        logs.append(AuditLog.from_dict(doc.to_dict()))
    
    return logs
