"""
Production configuration for Flask application
Optimized for security, performance, and reliability
"""

import os
from datetime import timedelta


class ProductionConfig:
    """Production configuration settings"""
    
    # Flask Configuration
    ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
    SESSION_COOKIE_NAME = 'zt_session'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set in production")
    
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES', 60))
    REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRATION_DAYS', 7))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        raise ValueError("CORS_ORIGINS must be set in production (no wildcards allowed)")
    
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-CSRF-Token']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
    
    # Email Configuration
    EMAIL_NOTIFICATIONS_ENABLED = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    ALERT_EMAIL = os.getenv('ALERT_EMAIL')
    
    # Security Settings
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION_MINUTES = int(os.getenv('LOCKOUT_DURATION_MINUTES', 30))
    SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
    MFA_LOCKOUT_ATTEMPTS = int(os.getenv('MFA_LOCKOUT_ATTEMPTS', 3))
    
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY environment variable must be set in production")
    
    # Rate Limiting
    RATE_LIMIT_ACCESS_REQUESTS = os.getenv('RATE_LIMIT_ACCESS_REQUESTS', '100/hour')
    RATE_LIMIT_AUTH = os.getenv('RATE_LIMIT_AUTH', '10/minute')
    RATE_LIMIT_API = os.getenv('RATE_LIMIT_API', '1000/hour')
    
    # Redis URL for distributed rate limiting (optional)
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Request Size Limits
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH_MB', 1)) * 1024 * 1024  # Convert to bytes
    
    # TLS/HTTPS
    PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'https')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 90))
    
    # Monitoring
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    # Performance
    JSON_SORT_KEYS = False  # Faster JSON serialization
    JSONIFY_PRETTYPRINT_REGULAR = False  # Compact JSON responses
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    @staticmethod
    def validate():
        """Validate that all required configuration is present"""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'ENCRYPTION_KEY',
            'CORS_ORIGINS',
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True


class DevelopmentConfig:
    """Development configuration settings"""
    
    ENV = 'development'
    DEBUG = True
    TESTING = False
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key-change-in-production')
    
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
    
    EMAIL_NOTIFICATIONS_ENABLED = False
    
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        ProductionConfig.validate()
        return ProductionConfig
    else:
        return DevelopmentConfig
