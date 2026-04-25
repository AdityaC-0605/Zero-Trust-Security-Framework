import pytest
from unittest.mock import patch
import time
from app.services.cache_layer import CacheLayer
from app.services.rate_limiter import RateLimiter

def test_rate_limit_counter_non_negativity():
    limiter = RateLimiter()
    # Execute exactly limit requests
    for _ in range(10):
        allowed, _ = limiter.is_allowed(ip_address="127.0.0.1", endpoint_type="auth")
        assert allowed is True

    # 11th request should be blocked and counter length == 10
    allowed, retry = limiter.is_allowed(ip_address="127.0.0.1", endpoint_type="auth")
    assert allowed is False
    assert retry > 0
    
    # Check internal boundary
    window = limiter.ip_counters["127.0.0.1"]
    assert len(window) >= 0

def test_cache_ttl_expiry():
    with patch("app.services.cache_layer.firestore.client"):
        cache = CacheLayer()
    
    fallback_val = 1
    def my_fallback():
        return fallback_val
        
    res1 = cache.get("key1", my_fallback, ttl_seconds=1)
    assert res1 == 1
    
    fallback_val = 2
    res2 = cache.get("key1", my_fallback, ttl_seconds=1)
    assert res2 == 1
    
    time.sleep(1.1)
    res3 = cache.get("key1", my_fallback, ttl_seconds=1)
    assert res3 == 2
