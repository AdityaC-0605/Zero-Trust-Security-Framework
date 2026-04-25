import pytest
from unittest.mock import patch, MagicMock
from app.services.jit_engine import JITEngineService

@pytest.fixture
def jit_engine():
    with patch("app.services.jit_engine.firestore.client"):
        yield JITEngineService()

# 5.3 Property 5: Confidence Score Bounds
def test_confidence_score_bounds(jit_engine):
    score_low = jit_engine.compute_confidence(0.0, 0.0, 0.0, 0.0, 0.0)
    assert score_low == 0.0
    
    score_high = jit_engine.compute_confidence(1.0, 1.0, 1.0, 1.0, 0.0)
    assert score_high == 1.0
    
# 5.4 Property 6: JIT Decision Completeness
def test_decision_completeness(jit_engine):
    jit_engine.compute_confidence = MagicMock()
    
    jit_engine.compute_confidence.return_value = 0.9
    assert jit_engine.process_request("1", 0,0,0,0) == "auto-grant"
    
    jit_engine.compute_confidence.return_value = 0.8
    assert jit_engine.process_request("1", 0,0,0,0) == "auto-grant"

    jit_engine.compute_confidence.return_value = 0.79
    assert jit_engine.process_request("1", 0,0,0,0) == "route-to-admin"
    
    jit_engine.compute_confidence.return_value = 0.5
    assert jit_engine.process_request("1", 0,0,0,0) == "route-to-admin"

    jit_engine.compute_confidence.return_value = 0.49
    assert jit_engine.process_request("1", 0,0,0,0) == "auto-deny"

    jit_engine.compute_confidence.return_value = 0.0
    assert jit_engine.process_request("1", 0,0,0,0) == "auto-deny"
    

# 5.5 Unit tests for JIT Engine
def test_ml_adjustment_clamping(jit_engine):
    score1 = jit_engine.compute_confidence(1.0, 0.0, 0.0, 0.0, 0.5)
    assert score1 == pytest.approx(0.4)
    
    score2 = jit_engine.compute_confidence(1.0, 0.0, 0.0, 0.0, -0.5)
    assert score2 == pytest.approx(0.2)

def test_weight_reload(jit_engine):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"identity": 0.5, "device_trust": 0.0, "behavioral_ctx": 0.0, "policy_compliance": 0.5}
    jit_engine.db.collection().document().get.return_value = mock_doc
    
    jit_engine.reload_weights()
    assert jit_engine._weights["identity"] == 0.5
    assert jit_engine._weights["device_trust"] == 0.0

def test_expiry_revocation(jit_engine):
    mock_doc = MagicMock()
    mock_doc.id = "grant1"
    
    jit_engine.db.collection().where().where().stream.return_value = [mock_doc]
    
    jit_engine.auto_revoke_expired()
    mock_doc.reference.update.assert_called_once()
    
    assert "status" in mock_doc.reference.update.call_args[0][0]
    assert mock_doc.reference.update.call_args[0][0]["status"] == "revoked"
    
    jit_engine.db.collection("audit_logs").add.assert_called_once()
