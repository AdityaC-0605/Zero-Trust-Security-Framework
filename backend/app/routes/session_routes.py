"""Session Management Routes"""
from flask import Blueprint, request, jsonify
from app.services.session_management import session_management

session_bp = Blueprint('session', __name__, url_prefix='/api/session')

@session_bp.route('/create', methods=['POST'])
def create_session():
    data = request.get_json()
    session = session_management.create_session_with_risk(
        data.get('user_id'),
        data.get('risk_score', 50)
    )
    return jsonify({'success': True, 'session': session}), 200

@session_bp.route('/monitor/<session_id>', methods=['GET'])
def monitor_session(session_id):
    result = session_management.monitor_session_risk(session_id)
    return jsonify({'success': True, 'session': result}), 200

@session_bp.route('/concurrent/<user_id>', methods=['GET'])
def check_concurrent(user_id):
    suspicious = session_management.detect_concurrent_sessions(user_id)
    return jsonify({'success': True, 'suspicious': suspicious}), 200
