"""
Behavioral Biometrics Routes
Handles behavioral data capture and analysis
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import os
from datetime import datetime
from app.models.behavioral_profile import BehavioralProfile
from app.models.behavioral_session import BehavioralSession
from app.services.audit_logger import log_audit_event

behavioral_bp = Blueprint('behavioral', __name__, url_prefix='/api/behavioral')

# Check if behavioral tracking is enabled
BEHAVIORAL_TRACKING_ENABLED = os.getenv('BEHAVIORAL_TRACKING_ENABLED', 'false').lower() == 'true'

def require_behavioral_enabled(f):
    """Decorator to check if behavioral tracking is enabled"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not BEHAVIORAL_TRACKING_ENABLED:
            return jsonify({
                'success': False,
                'message': 'Behavioral tracking is not enabled'
            }), 403
        return f(*args, **kwargs)
    return decorated_function


@behavioral_bp.route('/capture', methods=['POST'])
@require_behavioral_enabled
def capture_behavioral_data():
    """
    Capture behavioral biometric data from frontend
    
    Expected payload:
    {
        "user_id": "string",
        "session_id": "string",
        "timestamp": number,
        "data": {
            "keystrokes": [...],
            "mouseMovements": [...],
            "clicks": [...],
            "scrolls": [...],
            "navigation": [...]
        },
        "metadata": {
            "sessionDuration": number,
            "userAgent": "string",
            "screenResolution": "string",
            "viewport": "string"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        behavioral_data = data.get('data', {})
        metadata = data.get('metadata', {})
        
        if not user_id or not session_id:
            return jsonify({
                'success': False,
                'message': 'user_id and session_id are required'
            }), 400
        
        # Get or create behavioral session
        session = BehavioralSession.get_by_session_id(session_id)
        
        if not session:
            # Create new session
            session = BehavioralSession.create_session(
                session_id=session_id,
                user_id=user_id,
                keystroke_data=behavioral_data.get('keystrokes', []),
                mouse_data=behavioral_data.get('mouseMovements', []),
                click_data=behavioral_data.get('clicks', []),
                scroll_data=behavioral_data.get('scrolls', []),
                navigation_data=behavioral_data.get('navigation', []),
                metadata=metadata
            )
        else:
            # Append to existing session
            session.append_behavioral_data(
                keystroke_data=behavioral_data.get('keystrokes'),
                mouse_data=behavioral_data.get('mouseMovements'),
                click_data=behavioral_data.get('clicks'),
                scroll_data=behavioral_data.get('scrolls'),
                navigation_data=behavioral_data.get('navigation')
            )
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Failed to save behavioral data'
            }), 500
        
        # Log audit event
        log_audit_event(
            user_id=user_id,
            action='behavioral_data_captured',
            resource_type='behavioral_session',
            resource_id=str(session_id),
            details={
                'keystroke_count': len(behavioral_data.get('keystrokes', [])),
                'mouse_movement_count': len(behavioral_data.get('mouseMovements', [])),
                'click_count': len(behavioral_data.get('clicks', [])),
                'scroll_count': len(behavioral_data.get('scrolls', [])),
                'navigation_count': len(behavioral_data.get('navigation', []))
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Behavioral data captured successfully',
            'session_id': str(session_id),
            'data_points': session.get_activity_count()
        }), 200
        
    except Exception as e:
        print(f"Error capturing behavioral data: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/profile/<user_id>', methods=['GET'])
@require_behavioral_enabled
def get_behavioral_profile(user_id):
    """Get behavioral profile for a user"""
    try:
        profile = BehavioralProfile.get_by_user_id(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Behavioral profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': {
                'user_id': profile.user_id,
                'baseline_established': profile.baseline_established,
                'baseline_data_points': profile.baseline_data_points,
                'last_updated': profile.last_updated.isoformat() if profile.last_updated else None,
                'created_at': profile.created_at.isoformat() if profile.created_at else None
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting behavioral profile: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/session/<session_id>', methods=['GET'])
@require_behavioral_enabled
def get_behavioral_session(session_id):
    """Get behavioral session data"""
    try:
        session = BehavioralSession.get_by_session_id(session_id)
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Behavioral session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'risk_score': session.risk_score,
                'anomalies': session.anomalies,
                'session_duration': session.get_session_duration(),
                'activity_count': session.get_activity_count(),
                'session_start': session.session_start.isoformat() if session.session_start else None,
                'last_activity': session.last_activity.isoformat() if session.last_activity else None
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting behavioral session: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/sessions/user/<user_id>', methods=['GET'])
@require_behavioral_enabled
def get_user_sessions(user_id):
    """Get recent behavioral sessions for a user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions = BehavioralSession.get_by_user_id(user_id, limit=limit)
        
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session.session_id,
                'risk_score': session.risk_score,
                'anomalies_count': len(session.anomalies),
                'session_duration': session.get_session_duration(),
                'activity_count': session.get_activity_count(),
                'session_start': session.session_start.isoformat() if session.session_start else None,
                'last_activity': session.last_activity.isoformat() if session.last_activity else None
            })
        
        return jsonify({
            'success': True,
            'sessions': session_list,
            'count': len(session_list)
        }), 200
        
    except Exception as e:
        print(f"Error getting user sessions: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/risk-score/<session_id>', methods=['GET'])
@require_behavioral_enabled
def get_risk_score(session_id):
    """Get risk score for a behavioral session"""
    try:
        from app.services.behavioral_biometrics import behavioral_service
        
        session = BehavioralSession.get_by_session_id(session_id)
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        # Calculate risk score
        risk_data = behavioral_service.calculate_risk_score(session.user_id, session)
        
        # Update session with risk score
        if risk_data.get('baseline_available'):
            session.update_risk_score(risk_data['risk_score'])
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'risk_data': risk_data
        }), 200
        
    except Exception as e:
        print(f"Error getting risk score: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/anomalies/<session_id>', methods=['GET'])
@require_behavioral_enabled
def detect_anomalies(session_id):
    """Detect anomalies in a behavioral session"""
    try:
        from app.services.behavioral_biometrics import behavioral_service
        
        session = BehavioralSession.get_by_session_id(session_id)
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        # Detect anomalies
        anomaly_data = behavioral_service.detect_anomaly(session.user_id, session)
        
        # Update session with anomalies
        if anomaly_data.get('anomalies_detected'):
            session.update_risk_score(
                anomaly_data['overall_risk'],
                anomaly_data['anomalies']
            )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'anomaly_data': anomaly_data
        }), 200
        
    except Exception as e:
        print(f"Error detecting anomalies: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/train-model/<user_id>', methods=['POST'])
@require_behavioral_enabled
def train_user_model(user_id):
    """Train behavioral model for a user"""
    try:
        from app.services.behavioral_biometrics import behavioral_service
        
        # Train model
        success = behavioral_service.train_user_model(user_id)
        
        if success:
            log_audit_event(
                user_id=user_id,
                action='behavioral_model_trained',
                resource_type='ml_model',
                resource_id=f'behavioral_model_{user_id}',
                details={'training_status': 'success'}
            )
            
            return jsonify({
                'success': True,
                'message': 'Model trained successfully',
                'user_id': user_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to train model. Not enough data or ML libraries not available.'
            }), 400
        
    except Exception as e:
        print(f"Error training model: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/check-session-risk', methods=['POST'])
@require_behavioral_enabled
def check_session_risk_endpoint():
    """Check session risk and take appropriate action"""
    try:
        from app.services.session_monitor import session_monitor
        
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id or not session_id:
            return jsonify({
                'success': False,
                'message': 'user_id and session_id are required'
            }), 400
        
        # Check session risk
        result = session_monitor.check_session_risk(user_id, session_id)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        print(f"Error checking session risk: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@behavioral_bp.route('/status', methods=['GET'])
def get_behavioral_status():
    """Get behavioral tracking status"""
    return jsonify({
        'success': True,
        'enabled': BEHAVIORAL_TRACKING_ENABLED,
        'features': {
            'keystroke_dynamics': BEHAVIORAL_TRACKING_ENABLED,
            'mouse_dynamics': BEHAVIORAL_TRACKING_ENABLED,
            'navigation_patterns': BEHAVIORAL_TRACKING_ENABLED,
            'real_time_risk_scoring': BEHAVIORAL_TRACKING_ENABLED
        }
    }), 200
