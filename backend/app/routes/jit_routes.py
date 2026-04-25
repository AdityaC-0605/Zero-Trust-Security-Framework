import uuid
from flask import Blueprint, request, jsonify
from app.services.jit_engine import JITEngineService

jit_bp = Blueprint('jit_routes', __name__, url_prefix='/api/jit')
jit_service = None

def get_jit_service():
    global jit_service
    if not jit_service:
        jit_service = JITEngineService()
    return jit_service

@jit_bp.route('/request', methods=['POST'])
def submit_request():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
        
    req_id = str(uuid.uuid4())
    decision = get_jit_service().process_request(
        req_id,
        data.get("identity", 0.0),
        data.get("device_trust", 0.0),
        data.get("behavioral_ctx", 0.0),
        data.get("policy_compliance", 0.0),
        data.get("ml_adjustment", 0.0)
    )
    return jsonify({"request_id": req_id, "decision": decision}), 200

@jit_bp.route('/<req_id>/approve', methods=['POST'])
def approve_request(req_id):
    get_jit_service().db.collection("jit_requests").document(req_id).update({"decision": "manual-grant"})
    return jsonify({"message": f"Request {req_id} approved"}), 200

@jit_bp.route('/<req_id>/deny', methods=['POST'])
def deny_request(req_id):
    get_jit_service().db.collection("jit_requests").document(req_id).update({"decision": "manual-deny"})
    return jsonify({"message": f"Request {req_id} denied"}), 200

@jit_bp.route('/config', methods=['GET'])
def get_config():
    service = get_jit_service()
    return jsonify({
        "weights": service._weights,
        "last_updated": service.last_weight_update.isoformat()
    }), 200
