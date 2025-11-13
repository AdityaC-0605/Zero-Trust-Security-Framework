"""Security Assistant Routes"""
from flask import Blueprint, request, jsonify
from app.services.security_assistant import security_assistant

assistant_bp = Blueprint('assistant', __name__, url_prefix='/api/assistant')

@assistant_bp.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        query = data.get('query')
        user_id = data.get('user_id')
        
        response = security_assistant.generate_response(query)
        
        return jsonify({'success': True, 'response': response}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@assistant_bp.route('/explain-denial', methods=['POST'])
def explain_denial():
    try:
        data = request.get_json()
        reason = data.get('reason')
        
        explanation = security_assistant.explain_access_denial(reason)
        
        return jsonify({'success': True, 'explanation': explanation}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
