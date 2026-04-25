import pytest
from unittest.mock import patch, MagicMock
from app.services.continuous_auth_service import ContinuousAuthService

@pytest.fixture
def auth_service():
    with patch("app.services.continuous_auth_service.firestore.client"):
        yield ContinuousAuthService()

# 8.3 Property 9: Risk Score bounds
def test_risk_score_bounds(auth_service):
    baseline = {"metric1": {"mean": 100.0, "std": 10.0}}
    
    score1 = auth_service.compute_behavioral_risk_score({"metric1": 100.0}, baseline)
    assert 0.0 <= score1 <= 1.0

    score2 = auth_service.compute_behavioral_risk_score({"metric1": 250.0}, baseline)
    assert 0.0 <= score2 <= 1.0

def test_learning_mode(auth_service):
    doc_mock = MagicMock()
    doc_mock.exists = True
    doc_mock.to_dict.return_value = {
        "baseline": {"m1": {"mean": 0, "std": 1}},
        "learning_minutes_accumulated": 2 
    }
    auth_service.db.collection().document().get.return_value = doc_mock
    
    res = auth_service.process_behavioral_signals("sid", "uid", {"metrics": {"m1": 10}})
    assert res["status"] == "learning"
    assert res["risk_score"] == 0.0
    
def test_triggers(auth_service):
    doc_mock = MagicMock()
    doc_mock.exists = True
    doc_mock.to_dict.return_value = {
        "baseline": {"m1": {"mean": 100, "std": 5}},
        "learning_minutes_accumulated": 6
    }
    auth_service.db.collection().document().get.return_value = doc_mock
    
    res1 = auth_service.process_behavioral_signals("sid", "uid", {"metrics": {"m1": 105}})
    assert res1["action"] == "monitor"

    res2 = auth_service.process_behavioral_signals("sid", "uid", {"metrics": {"m1": 115}})
    assert res2["action"] == "step_up_auth"

    res3 = auth_service.process_behavioral_signals("sid", "uid", {"metrics": {"m1": 130}})
    assert res3["action"] == "terminate"

def test_ema_update(auth_service):
    metrics = {"m1": 200.0}
    baseline = {"m1": {"mean": 100.0, "std": 10.0}}
    
    updated = auth_service.apply_ema_update(metrics, baseline, alpha_ema=0.1)
    
    # new mean = 0.1*200 + 0.9*100 = 20 + 90 = 110
    assert updated["m1"]["mean"] == pytest.approx(110.0)
