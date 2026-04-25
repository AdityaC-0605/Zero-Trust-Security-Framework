import pytest
from unittest.mock import patch, MagicMock
from app.services.heatmap_service import HeatmapService
import time

@pytest.fixture
def heatmap_service():
    with patch("app.services.heatmap_service.firestore.client"):
        yield HeatmapService()

def test_layer_aggregation(heatmap_service):
    data = heatmap_service.aggregate_layers()
    
    assert "active_users" in data
    assert "visitors" in data
    assert "failed_auth" in data
    assert "threats" in data
    
def test_websocket_push_interval(heatmap_service):
    heatmap_service.push_interval = 0.1
    cb_mock = MagicMock()
    heatmap_service.register_subscriber(cb_mock)
    
    heatmap_service.start_push_loop()
    time.sleep(0.25)
    heatmap_service.stop_push_loop()
    
    # In 0.25s with 0.1s interval -> ~2 calls
    assert cb_mock.call_count >= 1
    
def test_drill_down_data_retrieval(heatmap_service):
    events = heatmap_service.get_zone_events("zoneB")
    
    assert len(events) == 2
    assert all(e["zone_id"] == "zoneB" for e in events)
