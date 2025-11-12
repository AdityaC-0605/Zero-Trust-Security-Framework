"""
Authentication Routes
API endpoints for user authentication, registration, and session management
"""

from flask import Blueprint, request, jsonify, make_response
from functools import wraps
from app.services.auth_service import auth_service
from app.models.user import create_user_document, get_user_by_id
from app.firebase_config import get_firestore_client
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
            # Verify session token
            payload = auth_service.verify_session_token(session_token)
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'AUTH_INVALID_TOKEN',
                    'message': str(e)
                }
            }), 401
    
    return decorated_function


@bp.route('/register', methods=['POST'])
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
        
        # Create session token
        session_token = auth_service.create_session(user_id, user.to_dict())
        
        # Record successful login
        auth_service.record_successful_login(user_id, ip_address, device_info)
        
        # Create response with HttpOnly cookie
        response = make_response(jsonify({
            'success': True,
            'sessionToken': session_token,
            'user': user.to_public_dict()
        }))
        
        # Set session token in HttpOnly, Secure, SameSite cookie
        response.set_cookie(
            'session_token',
            session_token,
            httponly=True,
            secure=True,  # Requires HTTPS in production
            samesite='Strict',
            max_age=60 * 60  # 60 minutes
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
def refresh():
    """
    Refresh session token
    
    Request Body:
        - idToken: Firebase ID token
    
    Returns:
        New session token
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
        
        # Refresh session
        session_token = auth_service.refresh_session(data['idToken'])
        
        # Get user data
        decoded_token = auth_service.verify_firebase_token(data['idToken'])
        user_id = decoded_token['uid']
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        
        # Create response with new cookie
        response = make_response(jsonify({
            'success': True,
            'sessionToken': session_token,
            'user': user.to_public_dict()
        }))
        
        response.set_cookie(
            'session_token',
            session_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=60 * 60
        )
        
        return response, 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'REFRESH_FAILED',
                'message': str(e)
            }
        }), 401


@bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout user and invalidate session
    
    Returns:
        Success message
    """
    try:
        # Create response
        response = make_response(jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }))
        
        # Clear session cookie
        response.set_cookie(
            'session_token',
            '',
            httponly=True,
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
