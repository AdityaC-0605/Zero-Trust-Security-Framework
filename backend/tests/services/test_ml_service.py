import pytest
from unittest.mock import patch, MagicMock
from app.services.ml_service import MLService

@pytest.fixture
def ml_service():
    with patch("app.services.ml_service.firestore.client"):
        yield MLService()

def test_ml_confidence_bounds(ml_service):
    res1 = ml_service.classify_intent("test string")
    assert 0.0 <= res1["confidence"] <= 1.0

    res2 = ml_service.predict_threat({"trust_score": -10.0, "resource_sensitivity": 50.0})
    assert 0.0 <= res2["threat_probability"] <= 1.0

    res3 = ml_service.detect_anomaly([500.0, -999.0])
    assert 0.0 <= res3["anomaly_score"] <= 1.0

def test_intent_classification_labels(ml_service):
    res_dest = ml_service.classify_intent("I want to delete everything rm -rf")
    assert res_dest["label"] == "destructive"
    
    res_benign = ml_service.classify_intent("just looking around")
    assert res_benign["label"] == "benign"

def test_threat_alert_emission(ml_service):
    ml_service.emit_high_threat_alert = MagicMock()
    
    ml_service.predict_threat({"trust_score": 0.0, "resource_sensitivity": 1.0, "recent_failed_attempts": 2})
    
    ml_service.emit_high_threat_alert.assert_called_once()

def test_model_deployment_gating(ml_service):
    ml_service.current_f1 = 0.80
    
    assert ml_service.deploy_new_model("model_v2", 0.75) is False
    assert ml_service.current_f1 == 0.80
    
    assert ml_service.deploy_new_model("model_v3", 0.85) is True
    assert ml_service.current_f1 == 0.85
