import datetime
import pytest
from unittest.mock import patch, MagicMock
from app.services.visitor_tracker import VisitorTrackerService

@pytest.fixture
def visitor_service():
    with patch("app.services.visitor_tracker.firestore.client"):
        yield VisitorTrackerService()

# 4.3 Property 8: Route Compliance Score Bounds
def test_compliance_score_bounds(visitor_service):
    score1 = visitor_service.compute_compliance_score(5, 10)
    assert 0.0 <= score1 <= 1.0
    
    score2 = visitor_service.compute_compliance_score(0, 10)
    assert 0.0 <= score2 <= 1.0

    score3 = visitor_service.compute_compliance_score(15, 10)
    assert 0.0 <= score3 <= 1.0
    
    score4 = visitor_service.compute_compliance_score(0, 0)
    assert 0.0 <= score4 <= 1.0

# 4.4 Unit tests for visitor tracker
def test_deviation_alert_threshold(visitor_service):
    visitor_service._emit_websocket_alert = MagicMock()
    
    route_points = [
        {"lat": 40.7128, "lon": -74.0060}
    ]
    
    res = visitor_service.check_deviation("v1", 40.7200, -74.0100, route_points)
    assert res is True
    visitor_service._emit_websocket_alert.assert_called_once()
    
    visitor_service._emit_websocket_alert.reset_mock()
    res2 = visitor_service.check_deviation("v1", 40.7129, -74.0060, route_points)
    assert res2 is False
    visitor_service._emit_websocket_alert.assert_not_called()

def test_predictive_alert_projection(visitor_service):
    visitor_service._emit_websocket_alert = MagicMock()
    
    t1 = datetime.datetime(2023, 1, 1, 12, 0, 0)
    t2 = datetime.datetime(2023, 1, 1, 12, 0, 1)
    
    history = [
        {"lat": 40.0, "lon": -74.0, "timestamp": t1},
        {"lat": 40.01, "lon": -74.0, "timestamp": t2} 
    ]
    
    restricted_zones = [
        {"id": "zone1", "lat": 40.61, "lon": -74.0, "radius_meters": 1000.0}
    ]
    
    res = visitor_service.predict_zone_entry("v1", history, restricted_zones)
    assert res is True
    visitor_service._emit_websocket_alert.assert_called_once()

    safe_zones = [
        {"id": "zone2", "lat": 41.0, "lon": -74.0, "radius_meters": 1000.0}
    ]
    visitor_service._emit_websocket_alert.reset_mock()
    res2 = visitor_service.predict_zone_entry("v1", history, safe_zones)
    assert res2 is False
    visitor_service._emit_websocket_alert.assert_not_called()
