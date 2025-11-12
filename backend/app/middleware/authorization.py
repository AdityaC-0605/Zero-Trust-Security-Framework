"""
Authorization Middleware
Role-based access control decorators for API endpoints
"""

from flask import request, jsonify
from functools import wraps
from app.services.auth_service import auth_service


def require_auth(f):
    """
    Decorator to require authentication for routes
    Verifies JWT session token and adds user_id and user_role to request
    """
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
            request.user_email = payload.get('email')
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


def require_role(*allowed_roles):
    """
    Decorator to require specific role(s) for routes
    Must be used after @require_auth decorator
    
    Usage:
        @require_role('admin')
        @require_role('admin', 'faculty')
    
    Args:
        *allowed_roles: Variable number of role strings
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user_role is set by require_auth
            if not hasattr(request, 'user_role'):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'AUTH_REQUIRED',
                        'message': 'Authentication required'
                    }
                }), 401
            
            # Check if user has required role
            if request.user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': f'Access denied. Required role: {", ".join(allowed_roles)}'
                    }
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_admin(f):
    """
    Decorator to require admin role
    Shorthand for @require_role('admin')
    """
    @wraps(f)
    @require_role('admin')
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function


def require_faculty_or_admin(f):
    """
    Decorator to require faculty or admin role
    Shorthand for @require_role('faculty', 'admin')
    """
    @wraps(f)
    @require_role('faculty', 'admin')
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    Get current authenticated user information from request
    Must be called within a route protected by @require_auth
    
    Returns:
        dict: User information (user_id, role, email)
        None: If not authenticated
    """
    if hasattr(request, 'user_id'):
        return {
            'user_id': request.user_id,
            'role': request.user_role,
            'email': getattr(request, 'user_email', None)
        }
    return None
