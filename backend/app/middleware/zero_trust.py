import os
import asyncio
import functools
import logging
from typing import Any
from flask import request, jsonify, make_response
from functools import wraps
from app.services.device_fingerprint_service import DeviceFingerprintService
from app.services.zero_trust_engine import zero_trust_engine
from app.services.audit_logger import audit_logger

logger = logging.getLogger(__name__)
device_service = DeviceFingerprintService()

def require_zero_trust(resource_name):
    """
    True Zero Trust Middleware.
    Enforces Identity + Device + Context before allowing access.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Authentication Check
            token = request.cookies.get("session_token")
            if not token:
                return jsonify({
                    "success": False,
                    "error": {"code": "AUTH_REQUIRED", "message": "Login required"}
                }), 401

            try:
                # Local verification as per auth_routes logic
                from app.routes.auth_routes import verify_session_token
                user = verify_session_token(token)
            except Exception as e:
                return jsonify({'success': False, 'error': {'code': 'AUTH_INVALID', 'message': str(e)}}), 401

            # Bind user to request
            request.user_id = user['uid']
            request.user_role = user.get('role', 'user')
            request.current_user = user

            # 2. Device Trust Assessment
            try:
                device_verified = device_service.verify_device(
                    user_id=request.user_id,
                    device_id=request.headers.get("X-Device-Id"),
                    fingerprint=request.headers.get("X-Device-Fingerprint")
                )
                
                # In development, we can be more lenient if the device is not yet fully registered
                if not device_verified and os.getenv("FLASK_ENV") == "development":
                    logger.warning(f"🔧 DEV MODE: Allowing unverified device for user {request.user_id}")
                    device_verified = True
                    
            except Exception as e:
                logger.error(f"Device verification error: {e}")
                device_verified = os.getenv("FLASK_ENV") == "development"

            if not device_verified:
                return jsonify({
                    "error": "Device not trusted",
                    "code": "DEVICE_UNTRUSTED",
                    "action": "register_device"
                }), 403
                
            # 3. Request Context
            mfa_header = request.headers.get('X-MFA-Verified', 'false').lower() == 'true'
            context_data = {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'is_mfa_verified': mfa_header,
                'path': request.path,
                'method': request.method
            }
            
            # 4. Central Engine
            is_allowed, reason, risk_score = zero_trust_engine.evaluate_access(
                user=user,
                device={'is_mismatch': not device_verified, 'trust_score': 100 if device_verified else 0},
                context=context_data,
                resource=resource_name
            )
            
            # 5. Policy Enforcement
            if not is_allowed:
                # Log denial
                audit_logger.log_access_attempt(
                    user_id=request.user_id,
                    resource=resource_name,
                    is_allowed=False,
                    details={
                        'reason': reason,
                        'risk_score': risk_score,
                        'device_id': request.headers.get('X-Device-Id'),
                        'ip': request.remote_addr
                    },
                    severity='high'
                )
                
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": reason,
                        "risk_score": risk_score
                    }
                }), 403
                
            # Log success
            audit_logger.log_access_attempt(
                user_id=request.user_id,
                resource=resource_name,
                is_allowed=True,
                details={
                    'reason': reason,
                    'risk_score': risk_score,
                    'device_id': request.headers.get('X-Device-Id'),
                    'ip': request.remote_addr
                },
                severity='low'
            )
            
            # 6. Execute actual route
            if asyncio.iscoroutinefunction(f):
                from app.middleware.zero_trust import run_async
                return run_async(f(*args, **kwargs))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def run_async(coro):
    """Helper to run async functions in sync Flask context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)
