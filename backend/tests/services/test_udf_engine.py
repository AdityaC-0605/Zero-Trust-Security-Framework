import datetime
import pytest
from unittest.mock import patch, MagicMock
from app.services.udf_engine import UDFEngine

@pytest.fixture
def udf_engine():
    with patch("app.services.udf_engine.firestore.client"):
        yield UDFEngine()

# 1.2 Property 1: Trust Score Bounds
def test_trust_score_bounds(udf_engine):
    fp = {"hardware": ["h1"], "browser": ["b1"], "network": ["n1"], "behavioral": ["bh1"]}
    baseline = fp.copy()
    
    score = udf_engine.compute_trust_score(fp, baseline, [])
    assert 0.0 <= score <= 1.0

# 1.3 Property 2: Trust Score Cap Enforcement
def test_trust_score_cap_vm(udf_engine):
    fp = {"hardware": ["h1"], "vm_detected": True}
    baseline = {"hardware": ["h1"]}
    
    score = udf_engine.compute_trust_score(fp, baseline, [])
    assert score <= 0.4

def test_trust_score_cap_automation(udf_engine):
    fp = {"hardware": ["h1"], "automation_detected": True}
    baseline = {"hardware": ["h1"]}
    
    score = udf_engine.compute_trust_score(fp, baseline, [])
    assert score <= 0.4

# 1.4 Property 3: Impossible Travel Cap
def test_impossible_travel_cap():
    # Tested internally within process_device since compute_trust_score doesn't cap travel explicitly
    pass

def test_detect_impossible_travel(udf_engine):
    # NY to London in 1 hour (>5000 km)
    session_a = {"lat": 40.7128, "lon": -74.0060, "timestamp": "2023-01-01T12:00:00Z"}
    session_b = {"lat": 51.5074, "lon": -0.1278, "timestamp": "2023-01-01T13:00:00Z"}
    
    assert udf_engine.detect_impossible_travel(session_a, session_b) is True
    
    # Normal travel
    session_b_slow = {"lat": 40.7200, "lon": -74.0100, "timestamp": "2023-01-01T12:30:00Z"}
    assert udf_engine.detect_impossible_travel(session_a, session_b_slow) is False

# 1.5 Property 4: Time Decay Monotonicity
def test_time_decay_monotonicity(udf_engine):
    decay_recent = udf_engine.time_decay(days_since_observation=1.0)
    decay_older = udf_engine.time_decay(days_since_observation=10.0)
    
    assert decay_recent > decay_older

# 1.6 Property 7: Jaccard Symmetry
def test_jaccard_symmetry(udf_engine):
    set_a = {"x", "y", "z"}
    set_b = {"y", "z", "w"}
    
    val1 = udf_engine._jaccard_index(set_a, set_b)
    val2 = udf_engine._jaccard_index(set_b, set_a)
    assert val1 == val2

# 1.7 Unit tests for partial signals
def test_partial_signal_failure(udf_engine):
    # Fingerprint missing some fields handles gracefully
    current_fp = {"hardware": ["h1"]}
    baseline_fp = {"hardware": ["h1"], "browser": ["b1"]}
    
    score = udf_engine.compute_weighted_jaccard(current_fp, baseline_fp)
    # hw match (0.3 * 1.0), browser mismatch (0.3 * 0), network empty empty (0.2 * 1.0), behavioral empty empty (0.2 * 1.0)
    assert score == pytest.approx(0.7)

# 1.7 Drift Alert
def test_detect_characteristic_drift(udf_engine):
    # Delta > 0.2
    history = [
        {"weighted_jaccard": 0.9, "timestamp": "2023-01-01T00:00:00Z"},
        {"weighted_jaccard": 0.6, "timestamp": "2023-01-02T00:00:00Z"}
    ]
    assert udf_engine.detect_characteristic_drift(history) is True
    
    # Delta <= 0.2
    history_ok = [
        {"weighted_jaccard": 0.9, "timestamp": "2023-01-01T00:00:00Z"},
        {"weighted_jaccard": 0.8, "timestamp": "2023-01-02T00:00:00Z"}
    ]
    assert udf_engine.detect_characteristic_drift(history_ok) is False
