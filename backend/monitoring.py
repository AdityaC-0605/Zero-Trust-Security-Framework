"""
Monitoring and error tracking configuration for production
Supports Sentry and Firebase Crashlytics
"""

import os
import logging
from functools import wraps
from flask import request, g
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_sentry(app):
    """Initialize Sentry for error tracking"""
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if sentry_dsn and os.getenv('FLASK_ENV') == 'production':
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,
                environment=os.getenv('FLASK_ENV', 'production'),
                release=os.getenv('APP_VERSION', 'unknown'),
                before_send=filter_sensitive_data,
                ignore_errors=[
                    KeyboardInterrupt,
                    SystemExit,
                ]
            )
            logger.info("Sentry initialized successfully")
        except ImportError:
            logger.warning("Sentry SDK not installed. Install with: pip install sentry-sdk")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {str(e)}")


def filter_sensitive_data(event, hint):
    """Filter sensitive data from error reports"""
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        sensitive_headers = ['Authorization', 'Cookie', 'X-CSRF-Token']
        for header in sensitive_headers:
            if header in event['request']['headers']:
                event['request']['headers'][header] = '[Filtered]'
    
    # Remove sensitive environment variables
    if 'extra' in event and 'sys.argv' in event['extra']:
        del event['extra']['sys.argv']
    
    return event


def init_firebase_crashlytics():
    """Initialize Firebase Crashlytics for error tracking"""
    try:
        import firebase_admin
        from firebase_admin import crashlytics
        
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Crashlytics unavailable.")
            return None
        
        logger.info("Firebase Crashlytics available")
        return crashlytics
    except ImportError:
        logger.warning("Firebase Crashlytics not available")
        return None


def log_request_metrics(f):
    """Decorator to log request metrics"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.start_time = time.time()
        
        try:
            response = f(*args, **kwargs)
            
            # Log request metrics
            duration = time.time() - g.start_time
            logger.info(
                f"Request: {request.method} {request.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"IP: {request.remote_addr}"
            )
            
            return response
        except Exception as e:
            duration = time.time() - g.start_time
            logger.error(
                f"Request Failed: {request.method} {request.path} | "
                f"Duration: {duration:.3f}s | "
                f"Error: {str(e)} | "
                f"IP: {request.remote_addr}"
            )
            raise
    
    return decorated_function


def track_performance_metric(metric_name, value, tags=None):
    """Track custom performance metrics"""
    tags = tags or {}
    logger.info(f"Performance Metric: {metric_name} = {value} | Tags: {tags}")


def track_error(error, context=None):
    """Track errors with context"""
    context = context or {}
    logger.error(f"Error: {str(error)} | Context: {context}", exc_info=True)
    
    # Send to Sentry if available
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    except ImportError:
        pass


class HealthCheck:
    """Health check endpoint for monitoring"""
    
    @staticmethod
    def check_database():
        """Check Firestore connectivity"""
        try:
            from firebase_admin import firestore
            db = firestore.client()
            # Simple read operation
            db.collection('systemConfig').document('settings').get()
            return True, "Database connection OK"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    @staticmethod
    def check_memory():
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return False, f"High memory usage: {memory.percent}%"
            return True, f"Memory usage: {memory.percent}%"
        except ImportError:
            return True, "Memory check unavailable (psutil not installed)"
    
    @staticmethod
    def get_status():
        """Get overall health status"""
        checks = {
            'database': HealthCheck.check_database(),
            'memory': HealthCheck.check_memory(),
        }
        
        all_healthy = all(status for status, _ in checks.values())
        
        return {
            'status': 'healthy' if all_healthy else 'degraded',
            'checks': {
                name: {
                    'status': 'pass' if status else 'fail',
                    'message': message
                }
                for name, (status, message) in checks.items()
            }
        }


def init_monitoring(app):
    """Initialize all monitoring services"""
    init_sentry(app)
    init_firebase_crashlytics()
    
    # Add health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return HealthCheck.get_status()
    
    logger.info("Monitoring initialized")
