import pytest
from unittest.mock import patch, MagicMock
from app.services.break_glass_controller import BreakGlassController

@pytest.fixture
def bg_controller():
    with patch("app.services.break_glass_controller.firestore.client"):
        yield BreakGlassController()

# 6.3 Property 12: Session Recording Integrity
def test_session_recording_integrity(bg_controller):
    entries = [
        {"action": "read_logs", "timestamp": "2023-01-01T12:00:00Z"},
        {"action": "download_data", "timestamp": "2023-01-01T12:01:00Z"}
    ]
    
    hash1 = bg_controller.compute_sha256(entries)
    hash2 = bg_controller.compute_sha256(entries)
    
    assert hash1 == hash2
    
def test_approval_flow(bg_controller):
    doc_mock = MagicMock()
    doc_mock.exists = True
    doc_mock.to_dict.return_value = {"level": 3}
    bg_controller.db.collection().document().get.return_value = doc_mock
    
    res_fail = bg_controller.approve_request("req1", "a1", "junior_admin")
    assert res_fail is False
    
    res_success = bg_controller.approve_request("req1", "a2", "senior_admin")
    assert res_success is True
    
def test_suspicious_activity_detection(bg_controller):
    bg_controller._emit_websocket_alert = MagicMock()
    doc_mock = MagicMock()
    doc_mock.to_dict.return_value = {"justification": "I just need to read some application logs to debug."}
    bg_controller.db.collection().document().get.return_value = doc_mock
    
    bg_controller.record_session_action("req1", "delete_db_table_users")
    bg_controller._emit_websocket_alert.assert_called_once()
    
def test_report_generation_timing(bg_controller):
    import time
    start = time.time()
    pdf_bytes = bg_controller.generate_report("req1")
    end = time.time()
    
    assert (end - start) < 30.0
    assert len(pdf_bytes) > 0
