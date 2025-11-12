# Audit Logging Integration Examples

This document shows how to integrate audit logging into existing routes and services.

## Authentication Routes Integration

### Example: Login with Audit Logging

```python
from app.services import audit_logger

@bp.route('/verify', methods=['POST'])
def verify():
    """Verify Firebase ID token and create session"""
    try:
        data = request.get_json()
        decoded_token = auth_service.verify_firebase_token(data['idToken'])
        user_id = decoded_token['uid']
        
        # Get user and check status
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        
        if not user or not user.is_active:
            # Log failed authentication
            audit_logger.log_authentication(
                user_id=user_id,
                success=False,
                ip_address=get_client_ip(),
                details={
                    'authMethod': 'password',
                    'reason': 'User not found or inactive'
                }
            )
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401
        
        # Create session
        session_token = auth_service.create_session(user_id, user.to_dict())
        
        # Log successful authentication
        audit_logger.log_authentication(
            user_id=user_id,
            success=True,
            ip_address=get_client_ip(),
            details={'authMethod': 'password'}
        )
        
        return jsonify({'success': True, 'sessionToken': session_token}), 200
        
    except Exception as e:
        # Log failed authentication
        if 'user_id' in locals():
            audit_logger.log_authentication(
                user_id=user_id,
                success=False,
                ip_address=get_client_ip(),
                details={
                    'authMethod': 'password',
                    'reason': str(e)
                }
            )
        return jsonify({'success': False, 'error': str(e)}), 401
```

### Example: MFA Verification with Audit Logging

```python
@bp.route('/mfa/verify', methods=['POST'])
@require_auth
def verify_mfa():
    """Verify MFA code"""
    try:
        data = request.get_json()
        user_id = request.user_id
        code = data['code']
        
        # Verify MFA code
        is_valid = auth_service.verify_mfa_code(user_id, code)
        
        # Log MFA event
        audit_logger.log_mfa_event(
            user_id=user_id,
            action='verify',
            success=is_valid,
            ip_address=get_client_ip(),
            details={'attempts': 1}
        )
        
        if is_valid:
            return jsonify({'success': True, 'verified': True}), 200
        else:
            return jsonify({'success': False, 'verified': False}), 400
            
    except Exception as e:
        # Log failed MFA verification
        audit_logger.log_mfa_event(
            user_id=request.user_id,
            action='verify',
            success=False,
            ip_address=get_client_ip(),
            details={'error': str(e)}
        )
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Access Request Routes Integration

### Example: Submit Access Request with Audit Logging

```python
from app.services import audit_logger, policy_engine

@bp.route('/request', methods=['POST'])
@require_auth
def submit_access_request():
    """Submit new access request"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        # Create access request
        access_request = create_access_request(
            db=get_firestore_client(),
            user_id=user_id,
            user_role=request.user_role,
            requested_resource=data['resource'],
            intent=data['intent'],
            duration=data['duration'],
            urgency=data['urgency'],
            ip_address=get_client_ip(),
            device_info=get_device_info()
        )
        
        # Evaluate request
        evaluation_result = policy_engine.evaluate_request(access_request.to_dict())
        
        # Update request with evaluation result
        access_request.set_evaluation_result(evaluation_result)
        update_access_request(
            db=get_firestore_client(),
            request_id=access_request.request_id,
            update_data=access_request.to_dict()
        )
        
        # Log access request
        audit_logger.log_access_request(
            request_data=access_request.to_dict(),
            decision=evaluation_result['decision'],
            confidence_score=evaluation_result['confidenceScore'],
            user_id=user_id,
            ip_address=get_client_ip()
        )
        
        return jsonify({
            'success': True,
            'requestId': access_request.request_id,
            'decision': evaluation_result['decision'],
            'confidenceScore': evaluation_result['confidenceScore']
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Admin Routes Integration

### Example: Update User Role with Audit Logging

```python
from app.services import audit_logger

@bp.route('/users/<user_id>', methods=['PUT'])
@require_auth
@require_admin
def update_user(user_id):
    """Update user account"""
    try:
        data = request.get_json()
        admin_id = request.user_id
        
        # Get current user data
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        old_role = user.role
        old_status = user.is_active
        
        # Update user
        update_data = {}
        if 'role' in data:
            update_data['role'] = data['role']
        if 'isActive' in data:
            update_data['isActive'] = data['isActive']
        
        update_user(db, user_id, update_data)
        
        # Log admin action
        audit_logger.log_admin_action(
            admin_id=admin_id,
            action='Update user',
            target_user_id=user_id,
            details={
                'previousRole': old_role,
                'newRole': data.get('role', old_role),
                'previousStatus': old_status,
                'newStatus': data.get('isActive', old_status)
            },
            ip_address=get_client_ip()
        )
        
        return jsonify({'success': True, 'message': 'User updated'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Example: Policy Change with Audit Logging

```python
@bp.route('/policy', methods=['POST'])
@require_auth
@require_admin
def create_or_update_policy():
    """Create or update policy"""
    try:
        data = request.get_json()
        admin_id = request.user_id
        policy_id = data.get('policyId')
        
        if policy_id:
            # Update existing policy
            old_policy = get_policy_by_id(get_firestore_client(), policy_id)
            update_policy(get_firestore_client(), policy_id, data)
            
            # Calculate changes
            changes = {}
            for key in ['minConfidence', 'mfaRequired', 'allowedRoles']:
                if key in data and data[key] != old_policy.to_dict().get(key):
                    changes[key] = {
                        'old': old_policy.to_dict().get(key),
                        'new': data[key]
                    }
            
            # Log policy change
            audit_logger.log_policy_change(
                admin_id=admin_id,
                policy_id=policy_id,
                action='update',
                changes=changes,
                ip_address=get_client_ip()
            )
            
            return jsonify({'success': True, 'message': 'Policy updated'}), 200
        else:
            # Create new policy
            policy = create_policy(get_firestore_client(), data)
            
            # Log policy creation
            audit_logger.log_policy_change(
                admin_id=admin_id,
                policy_id=policy.policy_id,
                action='create',
                changes={'policy': data},
                ip_address=get_client_ip()
            )
            
            return jsonify({'success': True, 'policyId': policy.policy_id}), 201
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Service Integration

### Example: Auth Service with Audit Logging

```python
# In auth_service.py

from app.services.audit_logger import audit_logger

class AuthService:
    def record_successful_login(self, user_id, ip_address, device_info):
        """Record successful login"""
        try:
            # Update user document
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'failedLoginAttempts': 0,
                'lockoutUntil': None,
                'lastLogin': datetime.utcnow(),
                'metadata.lastIpAddress': ip_address,
                'metadata.lastDeviceInfo': device_info
            })
            
            # Log authentication
            audit_logger.log_authentication(
                user_id=user_id,
                success=True,
                ip_address=ip_address,
                details={
                    'authMethod': 'password',
                    'deviceInfo': device_info
                }
            )
        except Exception as e:
            print(f"Error recording successful login: {str(e)}")
    
    def record_failed_login(self, user_id, ip_address):
        """Record failed login attempt"""
        try:
            # Update user document
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                failed_attempts = user_data.get('failedLoginAttempts', 0) + 1
                
                update_data = {
                    'failedLoginAttempts': failed_attempts,
                    'metadata.lastFailedLoginIp': ip_address,
                    'metadata.lastFailedLoginAt': datetime.utcnow()
                }
                
                # Lock account if threshold exceeded
                if failed_attempts >= self.max_login_attempts:
                    lockout_until = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
                    update_data['lockoutUntil'] = lockout_until
                
                user_ref.update(update_data)
                
                # Log failed authentication
                audit_logger.log_authentication(
                    user_id=user_id,
                    success=False,
                    ip_address=ip_address,
                    details={
                        'authMethod': 'password',
                        'attempts': failed_attempts,
                        'locked': failed_attempts >= self.max_login_attempts
                    }
                )
        except Exception as e:
            print(f"Error recording failed login: {str(e)}")
```

### Example: Policy Engine with Audit Logging

```python
# In policy_engine.py

from app.services.audit_logger import audit_logger

class PolicyEngine:
    def evaluate_request(self, request_data):
        """Evaluate access request"""
        try:
            # Perform evaluation
            result = self._perform_evaluation(request_data)
            
            # Log the evaluation (this will be called from the route)
            # The route will call audit_logger.log_access_request()
            
            return result
        except Exception as e:
            # Log error
            audit_logger.log_event(
                event_type='system_error',
                user_id=request_data.get('userId', 'unknown'),
                action='Policy evaluation failed',
                resource='policy_engine',
                result='failure',
                details={'error': str(e)},
                severity='high'
            )
            raise
```

## Best Practices

1. **Always log authentication events**: Both success and failure
2. **Log before and after state**: For updates, log old and new values
3. **Include context**: IP address, device info, user agent
4. **Set appropriate severity**: 
   - low: Normal operations
   - medium: Important actions (role changes, MFA events)
   - high: Security events (failed logins, denied access)
   - critical: Security breaches, system errors
5. **Handle errors gracefully**: Don't let logging failures break the main flow
6. **Sanitize sensitive data**: Never log passwords, tokens, or secrets

## Testing Integration

After integrating audit logging, test with:

```bash
# Run the application
python backend/run.py

# Make API calls and check logs
curl -X POST http://localhost:5000/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"idToken": "test_token"}'

# Check Firestore console for audit logs
# Or query programmatically:
python -c "
from app.services import audit_logger
logs = audit_logger.get_logs(limit=10)
for log in logs:
    print(f'{log[\"timestamp\"]}: {log[\"action\"]} - {log[\"result\"]}')
"
```
