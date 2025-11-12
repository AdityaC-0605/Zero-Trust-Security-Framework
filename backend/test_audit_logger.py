"""
Test script for Audit Logger
Tests the audit logging functionality
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.audit_logger import audit_logger
from app.models.audit_log import AuditLog


def test_log_event():
    """Test basic event logging"""
    print("\n=== Testing log_event ===")
    
    log = audit_logger.log_event(
        event_type='authentication',
        user_id='test_user_123',
        action='Login successful',
        resource='authentication_system',
        result='success',
        details={'authMethod': 'password'},
        ip_address='192.168.1.1',
        severity='low'
    )
    
    if log:
        print(f"✓ Event logged successfully: {log.log_id}")
        print(f"  Event Type: {log.event_type}")
        print(f"  Action: {log.action}")
        print(f"  Severity: {log.severity}")
    else:
        print("✗ Failed to log event")


def test_log_access_request():
    """Test access request logging"""
    print("\n=== Testing log_access_request ===")
    
    request_data = {
        'requestId': 'req_123',
        'requestedResource': 'lab_server',
        'intent': 'Need to run machine learning experiments for my thesis project',
        'duration': '7 days',
        'urgency': 'medium'
    }
    
    log = audit_logger.log_access_request(
        request_data=request_data,
        decision='granted',
        confidence_score=85.5,
        user_id='student_456',
        ip_address='192.168.1.2'
    )
    
    if log:
        print(f"✓ Access request logged successfully: {log.log_id}")
        print(f"  Decision: {request_data['requestedResource']}")
        print(f"  Confidence: 85.5")
    else:
        print("✗ Failed to log access request")


def test_log_authentication():
    """Test authentication logging"""
    print("\n=== Testing log_authentication ===")
    
    # Test successful login
    log_success = audit_logger.log_authentication(
        user_id='user_789',
        success=True,
        ip_address='192.168.1.3',
        details={'authMethod': 'password'}
    )
    
    if log_success:
        print(f"✓ Successful authentication logged: {log_success.log_id}")
    
    # Test failed login
    log_failure = audit_logger.log_authentication(
        user_id='user_789',
        success=False,
        ip_address='192.168.1.3',
        details={'authMethod': 'password', 'reason': 'Invalid password'}
    )
    
    if log_failure:
        print(f"✓ Failed authentication logged: {log_failure.log_id}")


def test_log_admin_action():
    """Test admin action logging"""
    print("\n=== Testing log_admin_action ===")
    
    log = audit_logger.log_admin_action(
        admin_id='admin_001',
        action='Update user role',
        target_user_id='user_456',
        details={
            'previousRole': 'student',
            'newRole': 'faculty'
        },
        ip_address='192.168.1.4'
    )
    
    if log:
        print(f"✓ Admin action logged successfully: {log.log_id}")
        print(f"  Action: Update user role")
        print(f"  Target: user_456")
    else:
        print("✗ Failed to log admin action")


def test_log_policy_change():
    """Test policy change logging"""
    print("\n=== Testing log_policy_change ===")
    
    log = audit_logger.log_policy_change(
        admin_id='admin_001',
        policy_id='policy_123',
        action='update',
        changes={
            'minConfidence': {'old': 70, 'new': 80},
            'mfaRequired': {'old': False, 'new': True}
        },
        ip_address='192.168.1.4'
    )
    
    if log:
        print(f"✓ Policy change logged successfully: {log.log_id}")
        print(f"  Policy: policy_123")
        print(f"  Action: update")
    else:
        print("✗ Failed to log policy change")


def test_log_mfa_event():
    """Test MFA event logging"""
    print("\n=== Testing log_mfa_event ===")
    
    # Test successful MFA setup
    log_setup = audit_logger.log_mfa_event(
        user_id='user_789',
        action='setup',
        success=True,
        ip_address='192.168.1.5'
    )
    
    if log_setup:
        print(f"✓ MFA setup logged: {log_setup.log_id}")
    
    # Test failed MFA verification
    log_verify = audit_logger.log_mfa_event(
        user_id='user_789',
        action='verify',
        success=False,
        ip_address='192.168.1.5',
        details={'attempts': 2}
    )
    
    if log_verify:
        print(f"✓ MFA verification failure logged: {log_verify.log_id}")


def test_high_severity_alert():
    """Test high-severity event that should trigger alert"""
    print("\n=== Testing high-severity alert ===")
    
    log = audit_logger.log_event(
        event_type='authentication',
        user_id='user_suspicious',
        action='Multiple failed login attempts',
        resource='authentication_system',
        result='failure',
        details={
            'attempts': 5,
            'reason': 'Account locked'
        },
        ip_address='192.168.1.100',
        severity='high'
    )
    
    if log:
        print(f"✓ High-severity event logged: {log.log_id}")
        print("  Alert should be sent (check email if configured)")
    else:
        print("✗ Failed to log high-severity event")


def test_audit_log_model():
    """Test AuditLog model validation"""
    print("\n=== Testing AuditLog model ===")
    
    # Test valid log
    log = AuditLog(
        event_type='access_request',
        user_id='user_123',
        action='Access granted',
        resource='lab_server',
        result='success',
        severity='low'
    )
    
    is_valid, error = log.validate()
    if is_valid:
        print("✓ Valid audit log created")
    else:
        print(f"✗ Validation failed: {error}")
    
    # Test invalid log (missing required field)
    invalid_log = AuditLog(
        event_type='',
        user_id='user_123',
        action='Test',
        resource='test',
        result='success'
    )
    
    is_valid, error = invalid_log.validate()
    if not is_valid:
        print(f"✓ Invalid log correctly rejected: {error}")
    else:
        print("✗ Invalid log was not rejected")


def test_get_logs():
    """Test retrieving logs with filters"""
    print("\n=== Testing get_logs ===")
    
    # Get all logs
    logs = audit_logger.get_logs(limit=10)
    print(f"✓ Retrieved {len(logs)} logs")
    
    # Get logs with filter
    filtered_logs = audit_logger.get_logs(
        filters={'eventType': 'authentication'},
        limit=5
    )
    print(f"✓ Retrieved {len(filtered_logs)} authentication logs")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Audit Logger Test Suite")
    print("=" * 60)
    
    try:
        test_audit_log_model()
        test_log_event()
        test_log_access_request()
        test_log_authentication()
        test_log_admin_action()
        test_log_policy_change()
        test_log_mfa_event()
        test_high_severity_alert()
        test_get_logs()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        print("\nNote: Some tests may show warnings if Firebase is not configured.")
        print("This is expected in a development environment.")
        
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
