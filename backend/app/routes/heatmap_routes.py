from flask import Blueprint, request, jsonify
from app.services.heatmap_service import HeatmapService

heatmap_bp = Blueprint('heatmap', __name__, url_prefix='/api/heatmap')
heatmap_service = None

def get_heatmap_service():
    global heatmap_service
    if not heatmap_service:
        heatmap_service = HeatmapService()
    return heatmap_service

@heatmap_bp.route('/zone/<zone_id>/events', methods=['GET'])
def get_zone_events(zone_id):
    events = get_heatmap_service().get_zone_events(zone_id)
    return jsonify({"events": events}), 200
