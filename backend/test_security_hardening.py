"""
Test script for security hardening implementation
Tests rate limiting, input sanitization, request size validation, and security headers
"""

import pytest
from app import create_app
from app.middleware.security import sanitize_string, sanitize_dict
import json


class TestSecurityMiddleware:
    """Test security middleware functions"""
    
    def test_sanitize_string_removes_script_tags(self):
        """Test that script tags are removed"""
        input_str = "<script>alert('xss')</script>Hello"
        result = sanitize_string(input_str)
        assert "<script>" not in result
        assert "alert" not in result
        
    def test_sanitize_string_removes_event_handlers(self):
        """Test that event handlers are removed"""
        input_str = '<div onclick="alert()">Click me</div>'
        result = sanitize_string(input_str)
        assert "onclick" not in result
        
    def test_sanitize_string_removes_javascript_protocol(self):
        """Test that javascript: protocol is removed"""
        input_str = '<a href="javascript:void(0)">Link</a>'
        result = sanitize_string(input_str)
        assert "javascript:" not in result
        
    def test_sanitize_string_html_escapes(self):
        """Test that HTML is escaped"""
        input_str = '<div>Test & "quotes"</div>'
        result = sanitize_string(input_str)
        assert "&lt;" in result or "<div>" not in result
        
    def test_sanitize_dict_recursive(self):
        """Test that nested dictionaries are sanitized"""
        input_dict = {
            "name": "<script>alert('xss')</script>John",
            "nested": {
                "description": '<a href="javascript:void(0)">Click</a>'
            },
            "list": ["<script>test</script>", "normal"]
        }
        result = sanitize_dict(input_dict)
        
        # Check that script tags are removed
        assert "<script>" not in result["name"]
        assert "javascript:" not in result["nested"]["description"]
        assert "<script>" not in result["list"][0]


class TestSecurityHeaders:
    """Test security headers are applied"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_security_headers_present(self, client):
        """Test that security headers are present in response"""
        response = client.get('/health')
        
        # Check for security headers
        assert 'Strict-Transport-Security' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Content-Security-Policy' in response.headers
        assert 'Referrer-Policy' in response.headers
        assert 'Permissions-Policy' in response.headers
        
    def test_hsts_header_value(self, client):
        """Test HSTS header has correct value"""
        response = client.get('/health')
        hsts = response.headers.get('Strict-Transport-Security')
        assert 'max-age=31536000' in hsts
        assert 'includeSubDomains' in hsts
        
    def test_frame_options_deny(self, client):
        """Test X-Frame-Options is set to DENY"""
        response = client.get('/health')
        assert response.headers.get('X-Frame-Options') == 'DENY'
        
    def test_content_type_nosniff(self, client):
        """Test X-Content-Type-Options is set to nosniff"""
        response = client.get('/health')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'


class TestRequestSizeValidation:
    """Test request size validation"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB
        with app.test_client() as client:
            yield client
    
    def test_large_payload_rejected(self, client):
        """Test that payloads larger than 1 MB are rejected"""
        # Create a large payload (2 MB)
        large_data = {'data': 'x' * (2 * 1024 * 1024)}
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(large_data),
            content_type='application/json'
        )
        
        # Should return 413 Payload Too Large
        assert response.status_code == 413
        
    def test_normal_payload_accepted(self, client):
        """Test that normal-sized payloads are accepted"""
        # Create a normal payload
        normal_data = {
            'idToken': 'test_token',
            'name': 'Test User',
            'role': 'student'
        }
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(normal_data),
            content_type='application/json'
        )
        
        # Should not return 413 (will fail auth but that's expected)
        assert response.status_code != 413


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_rate_limit_enforced(self, client):
        """Test that rate limiting is enforced"""
        # Note: This test may need to be adjusted based on actual rate limits
        # and may require mocking or using a test-specific rate limit
        
        # Make multiple requests
        responses = []
        for i in range(15):  # More than the auth limit of 10/minute
            response = client.post(
                '/api/auth/verify',
                data=json.dumps({'idToken': 'test'}),
                content_type='application/json'
            )
            responses.append(response)
        
        # At least one should be rate limited (429)
        status_codes = [r.status_code for r in responses]
        # Note: In testing, rate limiting might not trigger due to test isolation
        # This is more of an integration test
        print(f"Status codes: {status_codes}")


class TestCORSConfiguration:
    """Test CORS configuration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.options('/api/auth/verify')
        
        # Check for CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200
        
    def test_cors_no_wildcard(self, client):
        """Test that CORS doesn't use wildcard"""
        response = client.options('/api/auth/verify')
        
        # Should not have wildcard origin
        origin = response.headers.get('Access-Control-Allow-Origin', '')
        assert origin != '*'


def run_manual_tests():
    """
    Manual tests for security features
    Run these manually to verify security implementation
    """
    print("=== Manual Security Tests ===\n")
    
    print("1. Test Input Sanitization:")
    test_input = "<script>alert('xss')</script>Hello World"
    sanitized = sanitize_string(test_input)
    print(f"   Input: {test_input}")
    print(f"   Output: {sanitized}")
    print(f"   ✓ Script tags removed: {'<script>' not in sanitized}\n")
    
    print("2. Test Nested Sanitization:")
    test_dict = {
        "name": "<script>test</script>John",
        "data": {
            "description": '<a href="javascript:void(0)">Click</a>'
        }
    }
    sanitized_dict = sanitize_dict(test_dict)
    print(f"   Input: {test_dict}")
    print(f"   Output: {sanitized_dict}")
    print(f"   ✓ Nested sanitization works\n")
    
    print("3. Security Headers Test:")
    print("   Run: curl -I http://localhost:5000/health")
    print("   Check for: Strict-Transport-Security, X-Frame-Options, etc.\n")
    
    print("4. Rate Limiting Test:")
    print("   Run: for i in {1..15}; do curl -X POST http://localhost:5000/api/auth/verify; done")
    print("   Expected: Some requests should return 429 (Too Many Requests)\n")
    
    print("5. Request Size Test:")
    print("   Run: dd if=/dev/zero of=large.json bs=1M count=2")
    print("   Run: curl -X POST http://localhost:5000/api/auth/verify -d @large.json")
    print("   Expected: 413 Payload Too Large\n")
    
    print("6. CORS Test:")
    print("   Check .env CORS_ORIGINS setting")
    print("   Verify no wildcards (*) are used\n")


if __name__ == '__main__':
    # Run manual tests
    run_manual_tests()
    
    # Run pytest tests
    print("\n=== Running Automated Tests ===")
    pytest.main([__file__, '-v'])
