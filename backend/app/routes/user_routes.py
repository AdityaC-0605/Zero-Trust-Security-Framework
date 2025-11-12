"""
User Routes
API endpoints for user profile and management
"""

from flask import Blueprint, request, jsonify
from app.middleware.authorization import require_auth, require_role, require_admin, get_current_user
from app.models.user import get_user_by_id, update_user
from app.firebase_config import get_firestore_client

bp = Blueprint('users', __name__, url_prefix='/api/users')


@bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Get current user's profile
    
    Returns:
        User profile data
    """
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_public_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PROFILE_FETCH_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    Update current user's profile
    
    Request Body:
        - name: User name (optional)
        - department: User department (optional)
    
    Returns:
        Updated user profile
    """
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        data = request.get_json()
        
        # Only allow updating certain fields
        allowed_fields = ['name', 'department']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'No valid fields to update'
                }
            }), 400
        
        db = get_firestore_client()
        update_user(db, user_id, update_data)
        
        # Get updated user
        user = get_user_by_id(db, user_id)
        
        return jsonify({
            'success': True,
            'user': user.to_public_dict(),
            'message': 'Profile updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PROFILE_UPDATE_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/list', methods=['GET'])
@require_auth
@require_role('admin', 'faculty')
def list_users():
    """
    List all users (Admin and Faculty only)
    
    Query Parameters:
        - role: Filter by role (optional)
        - limit: Number of results (default: 50)
    
    Returns:
        List of users
    """
    try:
        db = get_firestore_client()
        
        # Get query parameters
        role_filter = request.args.get('role')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        users_ref = db.collection('users')
        
        if role_filter:
            query = users_ref.where('role', '==', role_filter).limit(limit)
        else:
            query = users_ref.limit(limit)
        
        # Execute query
        users = []
        for doc in query.stream():
            user_data = doc.to_dict()
            # Remove sensitive fields
            user_data.pop('mfaSecret', None)
            user_data.pop('failedLoginAttempts', None)
            user_data.pop('lockoutUntil', None)
            users.append(user_data)
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_LIST_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/<user_id>', methods=['GET'])
@require_auth
@require_admin
def get_user(user_id):
    """
    Get user by ID (Admin only)
    
    Args:
        user_id: User ID
    
    Returns:
        User data
    """
    try:
        db = get_firestore_client()
        user = get_user_by_id(db, user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_public_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_FETCH_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/<user_id>/deactivate', methods=['POST'])
@require_auth
@require_admin
def deactivate_user(user_id):
    """
    Deactivate user account (Admin only)
    
    Args:
        user_id: User ID
    
    Returns:
        Success message
    """
    try:
        current_user = get_current_user()
        
        # Prevent self-deactivation
        if current_user['user_id'] == user_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_OPERATION',
                    'message': 'Cannot deactivate your own account'
                }
            }), 400
        
        db = get_firestore_client()
        update_user(db, user_id, {'isActive': False})
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_DEACTIVATE_FAILED',
                'message': str(e)
            }
        }), 500


@bp.route('/<user_id>/activate', methods=['POST'])
@require_auth
@require_admin
def activate_user(user_id):
    """
    Activate user account (Admin only)
    
    Args:
        user_id: User ID
    
    Returns:
        Success message
    """
    try:
        db = get_firestore_client()
        update_user(db, user_id, {'isActive': True})
        
        return jsonify({
            'success': True,
            'message': 'User activated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_ACTIVATE_FAILED',
                'message': str(e)
            }
        }), 500
