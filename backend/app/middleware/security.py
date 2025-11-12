"""
Security middleware for the Zero Trust Security Framework
Implements rate limiting, input sanitization, request validation, and security headers
"""

from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import re
import html
import json
from collections import defaultdict
import threading

# Rate limiting storage (in-memory for simplicity, use Redis in production)
rate_limit_storage = defaultdict(list)
rate_limit_lock = threading.Lock()

# Maximum request payload size (1 MB)
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB in bytes

# Rate limit configurations
RATE_LIMITS = {
    'auth': {'requests': 10, 'window': 60},  # 10 requests per minute
    'access_request': {'requests': 100, 'window': 3600},  # 100 requests per hour
    'default': {'requests': 1000, 'window': 3600}  # 1000 requests per hour
}


def add_security_headers(response):
    """
    Add security headers to all responses
    Implements HSTS, X-Frame-Options, Content-Security-Policy, etc.
    """
    # HTTP Strict Transport Security (HSTS)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS Protection (legacy but still useful)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy (formerly Feature-Policy)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "gyroscope=(), "
        "accelerometer=()"
    )
    
    return response


def rate_limit(limit_type='default'):
    """
    Rate limiting decorator
    
    Args:
        limit_type: Type of rate limit to apply ('auth', 'access_request', 'default')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address or user ID if authenticated)
            client_id = request.remote_addr
            if hasattr(g, 'user_id') and g.user_id:
                client_id = f"{g.user_id}:{request.remote_addr}"
            
            # Get rate limit configuration
            config = RATE_LIMITS.get(limit_type, RATE_LIMITS['default'])
            max_requests = config['requests']
            window_seconds = config['window']
            
            # Create unique key for this endpoint and client
            key = f"{limit_type}:{client_id}:{request.endpoint}"
            
            with rate_limit_lock:
                now = datetime.utcnow()
                cutoff_time = now - timedelta(seconds=window_seconds)
                
                # Clean old entries
                rate_limit_storage[key] = [
                    timestamp for timestamp in rate_limit_storage[key]
                    if timestamp > cutoff_time
                ]
                
                # Check if limit exceeded
                if len(rate_limit_storage[key]) >= max_requests:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'RATE_LIMIT_EXCEEDED',
                            'message': f'Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.'
                        }
                    }), 429
                
                # Add current request
                rate_limit_storage[key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_string(value):
    """
    Sanitize string input to prevent XSS attacks
    
    Args:
        value: String to sanitize
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value
    
    # HTML escape to prevent XSS
    sanitized = html.escape(value)
    
    # Remove potentially dangerous patterns
    # Remove script tags
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def sanitize_dict(data):
    """
    Recursively sanitize dictionary values
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    if isinstance(data, dict):
        return {key: sanitize_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return sanitize_string(data)
    else:
        return data


def validate_request_size():
    """
    Middleware to validate request payload size
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Content-Length header
            content_length = request.content_length
            if content_length and content_length > MAX_CONTENT_LENGTH:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'PAYLOAD_TOO_LARGE',
                        'message': f'Request payload too large. Maximum size is {MAX_CONTENT_LENGTH / (1024 * 1024)} MB.'
                    }
                }), 413
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_input():
    """
    Middleware to sanitize all input data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Sanitize JSON body
            if request.is_json:
                try:
                    data = request.get_json()
                    if data:
                        sanitized_data = sanitize_dict(data)
                        # Store sanitized data in g for access in route handlers
                        g.sanitized_data = sanitized_data
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'INVALID_JSON',
                            'message': 'Invalid JSON payload'
                        }
                    }), 400
            
            # Sanitize query parameters
            sanitized_args = {}
            for key, value in request.args.items():
                sanitized_args[key] = sanitize_string(value)
            g.sanitized_args = sanitized_args
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json_schema(schema):
    """
    Validate request JSON against a schema
    
    Args:
        schema: Dictionary defining required fields and types
        Example: {'email': str, 'password': str, 'role': str}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_CONTENT_TYPE',
                        'message': 'Content-Type must be application/json'
                    }
                }), 400
            
            try:
                data = request.get_json()
            except Exception:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_JSON',
                        'message': 'Invalid JSON payload'
                    }
                }), 400
            
            # Validate required fields
            errors = {}
            for field, field_type in schema.items():
                if field not in data:
                    errors[field] = f'Field "{field}" is required'
                elif not isinstance(data[field], field_type):
                    errors[field] = f'Field "{field}" must be of type {field_type.__name__}'
            
            if errors:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Request validation failed',
                        'details': errors
                    }
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_sanitized_data():
    """
    Helper function to get sanitized request data
    
    Returns:
        Sanitized request data or original data if not sanitized
    """
    if hasattr(g, 'sanitized_data'):
        return g.sanitized_data
    return request.get_json() if request.is_json else {}


def get_sanitized_args():
    """
    Helper function to get sanitized query parameters
    
    Returns:
        Sanitized query parameters or original args if not sanitized
    """
    if hasattr(g, 'sanitized_args'):
        return g.sanitized_args
    return dict(request.args)
