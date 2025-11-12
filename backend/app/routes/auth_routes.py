"""
Authentication Routes
API endpoints for user authentication, registration, and session management
"""

from flask import Blueprint, request, jsonify, make_response
from functools import wraps
from app.services.auth_service import auth_service
from app.models.user import create_user_document, get_user_by_id
from app.firebase_config import get_firestore_client
from app.middleware.security import rate_limit, sanitize_input, validate_request_size, get_sanitized_data
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_client_ip():
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


def get_device_info():
    """Get device information from request headers"""
    return {
        'userAgent': request.headers.get('User-Agent', ''),
        'platform': request.headers.get('Sec-Ch-Ua-Platform', 'unknown'),
        'browser': request.headers.get('Sec-Ch-Ua', 'unknown')
    }


def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get session token from cookie
        session_token = request.cookies.get('session_token')
        
        if not session_token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_REQUIRED',
                    'message': 'Authentication required'
                }
            }), 401
        
        try:
            # Verify session token (includes inactivity check)
            payload = auth_service.verify_session_token(session_token, check_inactivity=True)
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            request.user_email = payload.get('email')
            return f(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            
            # Clear cookies if session is invalid
            response = make_response(jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_INVALID_TOKEN',
                    'message': error_message
                }
            }), 401)
            
            if "timeout" in error_message.lower() or "expired" in error_message.lower():
                response.set_cookie('session_token', '', max_age=0, httponly=True, secure=True, samesite='Strict')
                response.set_cookie('refresh_token', '', max_age=0, httponly=True, secure=True, samesite='Strict')
                response.set_cookie('csrf_token', '', max_age=0, samesite='Strict')
            
            return response
    
    return decorated_function


def require_csrf(f):
    """Decorator to require CSRF token for state-changing operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get CSRF token from header or form data
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not csrf_token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CSRF_TOKEN_MISSING',
                    'message': 'CSRF token required'
                }
            }), 403
        
        try:
            # Verify CSRF token
            user_id = request.user_id
            auth_service.verify_csrf_token(user_id, csrf_token)
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CSRF_TOKEN_INVALID',
                    'message': str(e)
                }
            }), 403
    
    return decorated_function


@bp.route('/register', methods=['POST'])
@rate_limit('auth')
@validate_request_size()
@sanitize_input()
def register():
    """
    Register new user
    
    Request Body:
        - idToken: Firebase ID token
        - name: User full name
        - role: User role (student, faculty, admin)
        - department: User department (optional)
        - studentId: Student ID (optional, required for students)
    
    Returns:
        User data and success message
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['idToken', 'name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': f'Missing required field: {field}'
                    }
                }), 400
        
        # Verify Firebase token
        decoded_token = auth_service.verify_firebase_token(data['idToken'])
        user_id = decoded_token['uid']
        email = decoded_token['email']
        
        # Create user document in Firestore
        db = get_firestore_client()
        user = create_user_document(
            db=db,
            user_id=user_id,
            email=email,
            role=data['role'],
            name=data['name'],
            department=data.get('department'),
            student_id=data.get('studentId')
        )
        
        return jsonify({
            'success': True,
            'user': user.to_public_dict(),
            'message': 'Registration successful. Please verify your email before logging in.'
        }), 201
    
    except Exception as e:
        error_message = str(e)
        status_code = 400
        
        if "already exists" in error_message.lower():
            error_code = 'USER_EXISTS'
        elif "validation failed" in error_message.lower():
            error_code = 'VALIDATION_ERROR'
        else:
            error_code = 'REGISTRATION_FAILED'
            status_code = 500
        
        return jsonify({
            'success': False,
            'error': {
                'code': error_code,
                'message': error_message
            }
        }), status_code


@bp.route('/verify', methods=['POST'])
@rate_limit('auth')
@validate_request_size()
@sanitize_input()
def verify():
    """
    Verify Firebase ID token and create session
    
    Request Body:
        - idToken: Firebase ID token
    
    Returns:
        Session token and user data
    """
    try:
        data = request.get_json()
        
        if 'idToken' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Missing idToken'
                }
            }), 400
        
        # Verify Firebase token
        decoded_token = auth_service.verify_firebase_token(data['idToken'])
        user_id = decoded_token['uid']
        
        # Get user from Firestore
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found. Please register first.'
                }
            }), 404
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_DISABLED',
                    'message': 'Account has been disabled'
                }
            }), 403
        
        # Get client info
        ip_address = get_client_ip()
        device_info = get_device_info()
        
        # Check login attempts
        try:
            auth_service.check_login_attempts(user_id, ip_address)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_ACCOUNT_LOCKED',
                    'message': str(e)
                }
            }), 403
        
        # Create session tokens (access, refresh, CSRF)
        tokens = auth_service.create_session(user_id, user.to_dict())
        
        # Record successful login
        auth_service.record_successful_login(user_id, ip_address, device_info)
        
        # Create response with HttpOnly cookies
        response = make_response(jsonify({
            'success': True,
            'sessionToken': tokens['accessToken'],
            'csrfToken': tokens['csrfToken'],
            'user': user.to_public_dict()
        }))
        
        # Set access token in HttpOnly, Secure, SameSite=Strict cookie
        response.set_cookie(
            'session_token',
            tokens['accessToken'],
            httponly=True,
            secure=True,  # Requires HTTPS in production
            samesite='Strict',
            max_age=60 * 60  # 60 minutes
        )
        
        # Set refresh token in HttpOnly, Secure, SameSite=Strict cookie
        response.set_cookie(
            'refresh_token',
            tokens['refreshToken'],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        # Set CSRF token in regular cookie (accessible to JavaScript)
        response.set_cookie(
            'csrf_token',
            tokens['csrfToken'],
            httponly=False,  # Needs to be accessible to JavaScript
            secure=True,
            samesite='Strict',
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return response, 200
    
    except Exception as e:
        # Record failed login if user exists
        try:
            if 'user_id' in locals():
                ip_address = get_client_ip()
                auth_service.record_failed_login(user_id, ip_address)
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'AUTH_FAILED',
                'message': str(e)
            }
        }), 401


@bp.route('/refresh', methods=['POST'])
@rate_limit('auth')
def refresh():
    """
    Refresh session token using refresh token (with token rotation)
    
    Returns:
        New session tokens
    """
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get('refresh_token')
        
        if not refresh_token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'REFRESH_TOKEN_MISSING',
                    'message': 'Refresh token required'
                }
            }), 401
        
        # Refresh session with token rotation
        tokens = auth_service.refresh_session_with_token(refresh_token)
        
        # Get user data
        payload = auth_service.verify_session_token(tokens['accessToken'], check_inactivity=False)
        user_id = payload['user_id']
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        
        # Create response with new cookies
        response = make_response(jsonify({
            'success': True,
            'sessionToken': tokens['accessToken'],
            'csrfToken': tokens['csrfToken'],
            'user': user.to_public_dict()
        }))
        
        # Set new access token
        response.set_cookie(
            'session_token',
            tokens['accessToken'],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=60 * 60
        )
        
        # Set new refresh token (token rotation)
        response.set_cookie(
            'refresh_token',
            tokens['refreshToken'],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=7 * 24 * 60 * 60
        )
        
        # Set new CSRF token
        response.set_cookie(
            'csrf_token',
            tokens['csrfToken'],
            httponly=False,
            secure=True,
            samesite='Strict',
            max_age=7 * 24 * 60 * 60
        )
        
        return response, 200
    
    except Exception as e:
        error_message = str(e)
        
        # Clear cookies on refresh failure
        response = make_response(jsonify({
            'success': False,
            'error': {
                'code': 'REFRESH_FAILED',
                'message': error_message
            }
        }), 401)
        
        response.set_cookie('session_token', '', max_age=0, httponly=True, secure=True, samesite='Strict')
        response.set_cookie('refresh_token', '', max_age=0, httponly=True, secure=True, samesite='Strict')
        response.set_cookie('csrf_token', '', max_age=0, samesite='Strict')
        
        return response


@bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout user and invalidate session
    
    Returns:
        Success message
    """
    try:
        user_id = request.user_id
        
        # Invalidate session in database
        auth_service.invalidate_session(user_id)
        
        # Create response
        response = make_response(jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }))
        
        # Clear all session cookies
        response.set_cookie(
            'session_token',
            '',
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=0
        )
        
        response.set_cookie(
            'refresh_token',
            '',
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=0
        )
        
        response.set_cookie(
            'csrf_token',
            '',
            httponly=False,
            secure=True,
            samesite='Strict',
            max_age=0
        )
        
        return response, 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LOGOUT_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/activity', methods=['POST'])
@require_auth
def update_activity():
    """
    Update last activity timestamp to prevent inactivity timeout
    
    Returns:
        Success message
    """
    try:
        user_id = request.user_id
        
        # Update last activity
        auth_service.update_last_activity(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Activity updated'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ACTIVITY_UPDATE_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/session/status', methods=['GET'])
@require_auth
def session_status():
    """
    Check session status and return remaining time
    
    Returns:
        Session status information
    """
    try:
        session_token = request.cookies.get('session_token')
        payload = auth_service.verify_session_token(session_token, check_inactivity=False)
        
        # Calculate remaining time
        exp_timestamp = payload.get('exp')
        iat_timestamp = payload.get('iat')
        last_activity_str = payload.get('last_activity')
        
        now = datetime.utcnow()
        expires_at = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
        issued_at = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None
        last_activity = datetime.fromisoformat(last_activity_str) if last_activity_str else None
        
        remaining_seconds = (expires_at - now).total_seconds() if expires_at else 0
        inactivity_seconds = (now - last_activity).total_seconds() if last_activity else 0
        inactivity_remaining = (auth_service.session_inactivity_minutes * 60) - inactivity_seconds
        
        return jsonify({
            'success': True,
            'session': {
                'active': True,
                'expiresAt': expires_at.isoformat() if expires_at else None,
                'issuedAt': issued_at.isoformat() if issued_at else None,
                'lastActivity': last_activity.isoformat() if last_activity else None,
                'remainingSeconds': max(0, int(remaining_seconds)),
                'inactivityRemainingSeconds': max(0, int(inactivity_remaining))
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SESSION_STATUS_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/mfa/setup', methods=['POST'])
@require_auth
def setup_mfa():
    """
    Setup MFA for user account
    
    Returns:
        MFA secret and QR code URI
    """
    try:
        user_id = request.user_id
        
        # Setup MFA
        mfa_data = auth_service.setup_mfa(user_id)
        
        return jsonify({
            'success': True,
            'secret': mfa_data['secret'],
            'qrCodeUri': mfa_data['qrCodeUri']
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'MFA_SETUP_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/mfa/verify', methods=['POST'])
@require_auth
@rate_limit('auth')
@validate_request_size()
@sanitize_input()
def verify_mfa():
    """
    Verify MFA code
    
    Request Body:
        - code: 6-digit TOTP code
    
    Returns:
        Verification result
    """
    try:
        data = request.get_json()
        
        if 'code' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Missing code'
                }
            }), 400
        
        user_id = request.user_id
        code = data['code']
        
        # Verify MFA code
        is_valid = auth_service.verify_mfa_code(user_id, code)
        
        if is_valid:
            return jsonify({
                'success': True,
                'verified': True,
                'message': 'MFA verification successful'
            }), 200
        else:
            return jsonify({
                'success': False,
                'verified': False,
                'error': {
                    'code': 'MFA_INVALID_CODE',
                    'message': 'Invalid MFA code'
                }
            }), 400
    
    except Exception as e:
        error_message = str(e)
        
        if "Account locked" in error_message:
            error_code = 'AUTH_ACCOUNT_LOCKED'
            status_code = 403
        else:
            error_code = 'MFA_VERIFICATION_FAILED'
            status_code = 500
        
        return jsonify({
            'success': False,
            'error': {
                'code': error_code,
                'message': error_message
            }
        }), status_code
