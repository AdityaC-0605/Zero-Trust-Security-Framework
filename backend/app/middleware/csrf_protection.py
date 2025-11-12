"""
CSRF Protection Middleware
Validates CSRF tokens on state-changing requests
"""

from flask import request, jsonify
from functools import wraps
from app.services.auth_service import auth_service


def require_csrf(f):
    """
    Decorator to require CSRF token for state-changing operations
    Must be used after require_auth decorator
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF check for GET, HEAD, OPTIONS requests
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)
        
        # Get CSRF token from header or form data
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not csrf_token:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CSRF_TOKEN_MISSING',
                    'message': 'CSRF token required for this operation'
                }
            }), 403
        
        try:
            # Verify CSRF token
            user_id = getattr(request, 'user_id', None)
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'AUTH_REQUIRED',
                        'message': 'Authentication required'
                    }
                }), 401
            
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
