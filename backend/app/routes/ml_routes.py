from flask import Blueprint, request, jsonify
from app.services.ml_service import MLService

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')
ml_service = None

def get_ml_service():
    global ml_service
    if not ml_service:
        ml_service = MLService()
    return ml_service

@ml_bp.route('/intent', methods=['POST'])
def intent_classification():
    data = request.get_json() or {}
    text = data.get("text", "")
    res = get_ml_service().classify_intent(text)
    return jsonify(res), 200

@ml_bp.route('/threat', methods=['POST'])
def threat_prediction():
    features = request.get_json() or {}
    res = get_ml_service().predict_threat(features)
    return jsonify(res), 200

@ml_bp.route('/anomaly', methods=['POST'])
def anomaly_detection():
    data = request.get_json() or {}
    features = data.get("features", [])
    res = get_ml_service().detect_anomaly(features)
    return jsonify(res), 200
