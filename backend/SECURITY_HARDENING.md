# Security Hardening Implementation

This document describes the security hardening measures implemented in the Zero Trust Security Framework.

## Overview

The application implements comprehensive security measures to protect against common vulnerabilities and attacks, following OWASP best practices and zero-trust principles.

## Implemented Security Measures

### 1. HTTPS/TLS Enforcement (Requirement 13.1)

**Implementation:**
- Production configuration enforces HTTPS through `PREFERRED_URL_SCHEME = 'https'`
- HSTS (HTTP Strict Transport Security) header with 1-year max-age
- Secure cookies require HTTPS in production
- TLS 1.2+ should be configured at the reverse proxy/load balancer level

**Deployment Configuration:**

For **Nginx** reverse proxy:
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # TLS 1.2+ only
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # SSL certificates
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

For **Apache** reverse proxy:
```apache
<VirtualHost *:443>
    ServerName your-domain.com
    
    # Enable SSL
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    # TLS 1.2+ only
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite HIGH:!aNULL:!MD5
    
    # Proxy to Flask app
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # Forward headers
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"
</VirtualHost>

# Redirect HTTP to HTTPS
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>
```

For **Cloud Platforms** (Heroku, Render, Google Cloud Run):
- HTTPS is automatically enforced
- Configure custom domain with SSL certificate
- Set environment variable: `FLASK_ENV=production`

### 2. Rate Limiting (Requirement 13.2)

**Implementation:**
- Authentication endpoints: 10 requests per minute per IP/user
- Access request endpoints: 100 requests per hour per user
- Default endpoints: 1000 requests per hour per IP

**Usage:**
```python
from app.middleware.security import rate_limit

@bp.route('/endpoint', methods=['POST'])
@rate_limit('auth')  # or 'access_request' or 'default'
def my_endpoint():
    pass
```

**Configuration:**
Rate limits are defined in `app/middleware/security.py`:
```python
RATE_LIMITS = {
    'auth': {'requests': 10, 'window': 60},  # 10 per minute
    'access_request': {'requests': 100, 'window': 3600},  # 100 per hour
    'default': {'requests': 1000, 'window': 3600}  # 1000 per hour
}
```

**Production Recommendation:**
For production, use Redis for distributed rate limiting:
```python
# Install: pip install redis
import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

redis_client = redis.from_url(os.getenv('REDIS_URL'))
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri=os.getenv('REDIS_URL')
)
```

### 3. Input Sanitization (Requirement 13.3)

**Implementation:**
- HTML escaping to prevent XSS attacks
- Removal of script tags and event handlers
- Removal of javascript: protocol
- Recursive sanitization of nested data structures

**Usage:**
```python
from app.middleware.security import sanitize_input, get_sanitized_data

@bp.route('/endpoint', methods=['POST'])
@sanitize_input()
def my_endpoint():
    data = get_sanitized_data()  # Returns sanitized request data
    pass
```

**What is sanitized:**
- All string values in JSON request bodies
- All query parameters
- Nested objects and arrays

**Example:**
```python
# Input
{
    "name": "<script>alert('xss')</script>John",
    "description": "Click <a href='javascript:void(0)' onclick='alert()'>here</a>"
}

# Output (sanitized)
{
    "name": "John",
    "description": "Click <a href='void(0)'>here</a>"
}
```

### 4. Request Size Validation (Requirement 13.4)

**Implementation:**
- Maximum payload size: 1 MB
- Enforced at Flask application level
- Returns 413 Payload Too Large error

**Configuration:**
```python
# In app/__init__.py
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB
```

**Usage:**
```python
from app.middleware.security import validate_request_size

@bp.route('/endpoint', methods=['POST'])
@validate_request_size()
def my_endpoint():
    pass
```

### 5. CORS Configuration (Requirement 13.5)

**Implementation:**
- Specific allowed origins only (no wildcards)
- Credentials support enabled
- Specific allowed headers and methods
- 1-hour preflight cache

**Configuration:**
Set allowed origins in `.env`:
```bash
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

**Features:**
- Automatically strips whitespace from origins
- Rejects wildcard (*) origins
- Falls back to localhost:3000 for development
- Supports credentials (cookies)

### 6. Security Headers (Requirement 13.5)

**Implemented Headers:**

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains | Force HTTPS for 1 year |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-XSS-Protection | 1; mode=block | Enable XSS filter |
| Content-Security-Policy | (see below) | Restrict resource loading |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer info |
| Permissions-Policy | (see below) | Disable unnecessary features |

**Content Security Policy:**
```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' data:;
connect-src 'self';
frame-ancestors 'none';
```

**Permissions Policy:**
```
geolocation=(), microphone=(), camera=(), payment=(),
usb=(), magnetometer=(), gyroscope=(), accelerometer=()
```

**Implementation:**
Headers are automatically added to all responses via `@app.after_request` decorator.

### 7. JSON Schema Validation

**Implementation:**
Optional decorator for strict JSON validation:

```python
from app.middleware.security import validate_json_schema

@bp.route('/endpoint', methods=['POST'])
@validate_json_schema({
    'email': str,
    'password': str,
    'role': str
})
def my_endpoint():
    pass
```

**Features:**
- Validates required fields
- Validates field types
- Returns detailed validation errors

## Security Best Practices

### For Developers

1. **Always use security decorators:**
   ```python
   @rate_limit('auth')
   @validate_request_size()
   @sanitize_input()
   ```

2. **Use sanitized data:**
   ```python
   data = get_sanitized_data()  # Not request.get_json()
   ```

3. **Validate input:**
   ```python
   if not data.get('field'):
       return error_response('VALIDATION_ERROR', 'Field required')
   ```

4. **Use CSRF protection for state-changing operations:**
   ```python
   @require_csrf
   def update_endpoint():
       pass
   ```

### For Deployment

1. **Set strong secrets:**
   ```bash
   SECRET_KEY=$(openssl rand -hex 32)
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Configure CORS properly:**
   ```bash
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Enable HTTPS:**
   - Use Let's Encrypt for free SSL certificates
   - Configure reverse proxy (Nginx/Apache)
   - Set `FLASK_ENV=production`

4. **Use Redis for rate limiting:**
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Monitor security logs:**
   - Check audit logs regularly
   - Set up alerts for high-severity events
   - Monitor rate limit violations

## Testing Security

### Test Rate Limiting
```bash
# Should succeed
for i in {1..10}; do curl -X POST http://localhost:5000/api/auth/verify; done

# Should fail with 429
curl -X POST http://localhost:5000/api/auth/verify
```

### Test Input Sanitization
```bash
curl -X POST http://localhost:5000/api/access/request \
  -H "Content-Type: application/json" \
  -d '{"intent": "<script>alert(\"xss\")</script>Test"}'
```

### Test Request Size Limit
```bash
# Generate 2MB file (should fail)
dd if=/dev/zero of=large.json bs=1M count=2
curl -X POST http://localhost:5000/api/access/request \
  -H "Content-Type: application/json" \
  -d @large.json
```

### Test Security Headers
```bash
curl -I https://yourdomain.com/api/health
# Check for security headers in response
```

## Compliance

This implementation addresses:
- **OWASP Top 10**: Injection, XSS, Broken Authentication, Security Misconfiguration
- **CWE-79**: Cross-site Scripting (XSS)
- **CWE-352**: Cross-Site Request Forgery (CSRF)
- **CWE-770**: Allocation of Resources Without Limits (Rate Limiting)
- **CWE-311**: Missing Encryption of Sensitive Data (HTTPS/TLS)

## Maintenance

### Regular Updates
- Update dependencies monthly: `pip install --upgrade -r requirements.txt`
- Review security advisories: `pip-audit`
- Update TLS certificates before expiration

### Monitoring
- Monitor rate limit violations
- Track failed authentication attempts
- Review audit logs for suspicious activity
- Set up alerts for security events

## References

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
