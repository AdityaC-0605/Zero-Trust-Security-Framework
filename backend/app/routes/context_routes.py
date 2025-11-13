"""Contextual Intelligence Routes"""
from flask import Blueprint, request, jsonify
from functools import wraps
import os
from datetime import datetime
from app.services.contextual_intelligence import contextual_intelligence
from app.models.device_profile import DeviceProfile

context_bp = Blueprint('context', __name__, url_prefix='/api/context')

CONTEXT_ENABLED = os.getenv('CONTEXT_EVALUATION_ENABLED', 'false').lower() == 'true'

def require_context_enabled(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not CONTEXT_ENABLED:
            return jsonify({'success': False, 'message': 'Context evaluation not enabled'}), 403
        return f(*args, **kwargs)
    return decorated

@context_bp.route('/evaluate', methods=['POST'])
@require_context_enabled
def evaluate_context():
    """Evaluate overall context score"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        device_info = data.get('device_info', {})
        network_info = data.get('network_info', {})
        
        result = contextual_intelligence.calculate_overall_context_score(
            user_id, device_info, network_info
        )
        
        return jsonify({'success': True, 'context': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@context_bp.route('/device-health', methods=['POST'])
@require_context_enabled
def evaluate_device_health():
    """Evaluate device health"""
    try:
        device_info = request.get_json()
        result = contextual_intelligence.evaluate_device_health(device_info)
        return jsonify({'success': True, 'device_health': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@context_bp.route('/network-security', methods=['POST'])
@require_context_enabled
def evaluate_network_security():
    """Evaluate network security"""
    try:
        network_info = request.get_json()
        result = contextual_intelligence.evaluate_network_security(network_info)
        return jsonify({'success': True, 'network_security': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@context_bp.route('/impossible-travel', methods=['POST'])
@require_context_enabled
def check_impossible_travel():
    """Check for impossible travel"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        location = data.get('location', {})
        
        result = contextual_intelligence.detect_impossible_travel(
            user_id, location, datetime.utcnow()
        )
        
        return jsonify({'success': True, 'impossible_travel': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@context_bp.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'success': True,
        'enabled': CONTEXT_ENABLED,
        'features': {
            'device_health': CONTEXT_ENABLED,
            'network_security': CONTEXT_ENABLED,
            'time_evaluation': CONTEXT_ENABLED,
            'impossible_travel': CONTEXT_ENABLED
        }
    }), 200
