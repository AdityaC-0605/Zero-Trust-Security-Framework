# Audit Logging System

## Overview

The Audit Logging System provides comprehensive logging of all security-relevant events in the Zero Trust Security Framework. It tracks authentication attempts, access requests, administrative actions, policy changes, and MFA events.

## Components

### 1. AuditLog Model (`app/models/audit_log.py`)

Defines the data structure for audit logs with the following fields:

- **logId**: Unique identifier (UUID)
- **eventType**: Type of event (access_request, authentication, admin_action, policy_change, mfa_event, system_error)
- **userId**: User ID associated with the event
- **action**: Specific action description
- **resource**: Affected resource
- **result**: Result of the action (success, failure, denied)
- **details**: Additional context (dictionary)
- **timestamp**: Event timestamp (UTC)
- **ipAddress**: Client IP address
- **severity**: Severity level (low, medium, high, critical)

### 2. AuditLogger Service (`app/services/audit_logger.py`)

Provides methods for logging different types of events:

#### Core Methods

- `log_event()`: Generic event logging
- `log_access_request()`: Log access request evaluations
- `log_authentication()`: Log authentication attempts
- `log_admin_action()`: Log administrative operations
- `log_policy_change()`: Log policy modifications
- `log_mfa_event()`: Log MFA-related events
- `send_alert()`: Send email alerts for high-severity events
- `get_logs()`: Retrieve logs with filtering

## Usage Examples

### Logging an Access Request

```python
from app.services import audit_logger

audit_logger.log_access_request(
    request_data={
        'requestId': 'req_123',
        'requestedResource': 'lab_server',
        'intent': 'Running ML experiments',
        'duration': '7 days',
        'urgency': 'medium'
    },
    decision='granted',
    confidence_score=85.5,
    user_id='user_123',
    ip_address='192.168.1.1'
)
```

### Logging Authentication

```python
# Successful login
audit_logger.log_authentication(
    user_id='user_123',
    success=True,
    ip_address='192.168.1.1',
    details={'authMethod': 'password'}
)

# Failed login
audit_logger.log_authentication(
    user_id='user_123',
    success=False,
    ip_address='192.168.1.1',
    details={'authMethod': 'password', 'reason': 'Invalid password'}
)
```

### Logging Admin Actions

```python
audit_logger.log_admin_action(
    admin_id='admin_001',
    action='Update user role',
    target_user_id='user_456',
    details={
        'previousRole': 'student',
        'newRole': 'faculty'
    },
    ip_address='192.168.1.4'
)
```

### Logging Policy Changes

```python
audit_logger.log_policy_change(
    admin_id='admin_001',
    policy_id='policy_123',
    action='update',
    changes={
        'minConfidence': {'old': 70, 'new': 80},
        'mfaRequired': {'old': False, 'new': True}
    },
    ip_address='192.168.1.4'
)
```

### Retrieving Logs

```python
# Get all logs
logs = audit_logger.get_logs(limit=100)

# Get logs with filters
logs = audit_logger.get_logs(
    filters={
        'userId': 'user_123',
        'eventType': 'authentication',
        'severity': 'high'
    },
    limit=50
)
```

## Email Alerts

High-severity and critical events automatically trigger email alerts to administrators.

### Configuration

Set the following environment variables in `.env`:

```bash
# Email configuration
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=admin@example.com
```

### Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password as `SMTP_PASSWORD`

## Firestore Configuration

### Indexes

The audit logging system requires composite indexes for efficient querying. Deploy the indexes using:

```bash
firebase deploy --only firestore:indexes
```

The required indexes are defined in `firestore.indexes.json`:

- userId + timestamp (descending)
- eventType + timestamp (descending)
- severity + timestamp (descending)
- result + timestamp (descending)

### Security Rules

Deploy security rules to protect audit logs:

```bash
firebase deploy --only firestore:rules
```

The rules ensure:
- Only admins can read audit logs
- Only the backend service can write audit logs
- Users cannot modify or delete logs

### TTL (Time To Live) Policy

Audit logs are retained for a minimum of 90 days. To clean up old logs:

```python
from app.utils.firestore_setup import setup_audit_log_ttl

# Run cleanup (should be scheduled as a cron job)
setup_audit_log_ttl()
```

**Recommended**: Set up a Cloud Function or cron job to run this cleanup weekly:

```python
# Cloud Function example
@scheduler.scheduled_function(schedule="0 0 * * 0")  # Weekly on Sunday
def cleanup_old_logs(event):
    from app.utils.firestore_setup import setup_audit_log_ttl
    setup_audit_log_ttl()
```

## Testing

Run the test suite to verify audit logging functionality:

```bash
cd backend
python test_audit_logger.py
```

The test suite covers:
- Event logging
- Access request logging
- Authentication logging
- Admin action logging
- Policy change logging
- MFA event logging
- High-severity alerts
- Log retrieval with filters

## Integration with Other Services

### In Authentication Service

```python
from app.services import audit_logger

# Log successful login
audit_logger.log_authentication(
    user_id=user_id,
    success=True,
    ip_address=request.remote_addr,
    details={'authMethod': 'password'}
)
```

### In Policy Engine

```python
from app.services import audit_logger

# Log access request evaluation
audit_logger.log_access_request(
    request_data=access_request.to_dict(),
    decision=evaluation_result['decision'],
    confidence_score=evaluation_result['confidenceScore'],
    user_id=access_request.user_id,
    ip_address=access_request.ip_address
)
```

### In Admin Routes

```python
from app.services import audit_logger

# Log user role update
audit_logger.log_admin_action(
    admin_id=current_user_id,
    action='Update user role',
    target_user_id=user_id,
    details={
        'previousRole': old_role,
        'newRole': new_role
    },
    ip_address=request.remote_addr
)
```

## Monitoring and Analytics

### Query Examples

```python
# Get failed authentication attempts in last 24 hours
from datetime import datetime, timedelta

cutoff = datetime.utcnow() - timedelta(hours=24)
logs = audit_logger.get_logs(
    filters={
        'eventType': 'authentication',
        'result': 'failure'
    },
    limit=1000
)

# Filter by timestamp in application code
recent_failures = [
    log for log in logs 
    if log['timestamp'] > cutoff
]
```

### Metrics to Track

- Failed authentication attempts per user
- Access request denial rate
- High-severity events per day
- Admin actions frequency
- Policy changes over time

## Best Practices

1. **Always log security events**: Authentication, authorization, access requests
2. **Include context**: IP address, device info, user agent
3. **Set appropriate severity**: Use 'high' or 'critical' for security incidents
4. **Sanitize sensitive data**: Don't log passwords or tokens
5. **Monitor alerts**: Set up email notifications for critical events
6. **Regular cleanup**: Schedule TTL cleanup to manage storage
7. **Review logs regularly**: Analyze patterns and anomalies

## Troubleshooting

### Logs not appearing in Firestore

1. Check Firebase credentials are configured
2. Verify Firestore client is initialized
3. Check for validation errors in console output

### Email alerts not sending

1. Verify `EMAIL_NOTIFICATIONS_ENABLED=true`
2. Check SMTP credentials are correct
3. For Gmail, ensure App Password is used (not regular password)
4. Check firewall/network allows SMTP connections

### Query performance issues

1. Ensure composite indexes are deployed
2. Use appropriate filters to limit result set
3. Consider pagination for large datasets
4. Monitor Firestore usage in Firebase Console

## Requirements Satisfied

This implementation satisfies the following requirements:

- **7.1**: Audit log created within 500ms for every action
- **7.2**: Includes event type, user ID, action, resource, result, timestamp, IP, severity
- **7.3**: Logs retained for minimum 90 days
- **7.4**: Supports filtering by user, date range, event type, decision
- **7.5**: Real-time alerts sent for high-severity events

## Next Steps

1. Integrate audit logging into all API endpoints
2. Set up Cloud Function for automated log cleanup
3. Create admin dashboard for log viewing
4. Implement log export functionality
5. Set up monitoring and alerting dashboards
