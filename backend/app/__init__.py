from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback
import sys

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev_jwt_secret')
    
    # Maximum request payload size (1 MB)
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
    
    # Initialize Redis for caching and session management
    try:
        from redis_config import init_redis
        redis_client = init_redis()
        app.config['REDIS_CLIENT'] = redis_client
        print("Redis initialized successfully")
    except Exception as e:
        print(f"Redis initialization failed: {e}")
        print("Application will continue without Redis caching")
        app.config['REDIS_CLIENT'] = None
    
    # Initialize WebSocket server
    try:
        from websocket_config import init_socketio
        socketio = init_socketio(app)
        app.config['SOCKETIO'] = socketio
        print("WebSocket server initialized successfully")
    except Exception as e:
        print(f"WebSocket initialization failed: {e}")
        print("Application will continue without WebSocket support")
        app.config['SOCKETIO'] = None
    
    # CORS configuration - specific origins only, no wildcards
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    # Strip whitespace and ensure no wildcards
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip() and '*' not in origin]
    
    # If no valid origins, default to localhost for development
    if not cors_origins:
        cors_origins = ['http://localhost:3000']
    
    CORS(app, 
         origins=cors_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Content-Type', 'Authorization'],
         max_age=3600)
    
    # Import security middleware
    from app.middleware.security import add_security_headers
    
    # Add security headers to all responses
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)
    
    # Import error handler utilities
    from app.utils.error_handler import AppError, create_error_response
    from app.services.audit_logger import audit_logger
    
    # Handle application errors
    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle custom application errors"""
        response, status_code = create_error_response(error, include_details=True)
        return jsonify(response), status_code
    
    # Handle request payload size errors
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle payload too large errors"""
        try:
            audit_logger.log_event(
                event_type='validation_error',
                user_id=getattr(request, 'user_id', None),
                action='request_payload_validation',
                resource=request.path,
                result='failure',
                details={'error': 'Payload too large', 'max_size': '1 MB'},
                severity='low'
            )
        except Exception as e:
            print(f"Failed to log error: {e}", file=sys.stderr)
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'PAYLOAD_TOO_LARGE',
                'message': 'Request payload too large. Maximum size is 1 MB.'
            }
        }), 413
    
    # Handle method not allowed
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle method not allowed errors"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'HTTP method not allowed for this endpoint'
            }
        }), 405
    
    # Handle not found
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Endpoint not found'
            }
        }), 404
    
    # Handle rate limit errors (429)
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit errors"""
        try:
            audit_logger.log_event(
                event_type='rate_limit_exceeded',
                user_id=getattr(request, 'user_id', None),
                action='rate_limit_check',
                resource=request.path,
                result='failure',
                details={'ip_address': request.remote_addr},
                severity='medium'
            )
        except Exception as e:
            print(f"Failed to log error: {e}", file=sys.stderr)
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Too many requests. Please try again later.'
            }
        }), 429
    
    # Handle internal server errors
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors"""
        stack_trace = traceback.format_exc()
        
        try:
            audit_logger.log_event(
                event_type='system_error',
                user_id=getattr(request, 'user_id', None),
                action='internal_error',
                resource=request.path,
                result='failure',
                details={
                    'error': str(error),
                    'stack_trace': stack_trace
                },
                severity='critical'
            )
        except Exception as e:
            print(f"Failed to log error: {e}", file=sys.stderr)
        
        # Print to stderr for debugging
        print(f"Internal server error: {error}", file=sys.stderr)
        print(stack_trace, file=sys.stderr)
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }
        }), 500
    
    # Handle all other exceptions
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        stack_trace = traceback.format_exc()
        
        try:
            audit_logger.log_event(
                event_type='system_error',
                user_id=getattr(request, 'user_id', None),
                action='unhandled_exception',
                resource=request.path,
                result='failure',
                details={
                    'error': str(error),
                    'error_type': type(error).__name__,
                    'stack_trace': stack_trace
                },
                severity='critical'
            )
        except Exception as e:
            print(f"Failed to log error: {e}", file=sys.stderr)
        
        # Print to stderr for debugging
        print(f"Unhandled exception: {error}", file=sys.stderr)
        print(stack_trace, file=sys.stderr)
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }
        }), 500
    
    # Register blueprints
    from app.routes import auth_routes, user_routes, access_routes, admin_routes, policy_routes, notification_routes, behavioral_routes, threat_routes, context_routes, assistant_routes, training_routes, session_routes, reports_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(access_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(policy_routes.bp)
    app.register_blueprint(notification_routes.bp)
    app.register_blueprint(behavioral_routes.behavioral_bp)
    app.register_blueprint(threat_routes.threat_bp)
    app.register_blueprint(context_routes.context_bp)
    app.register_blueprint(assistant_routes.assistant_bp)
    app.register_blueprint(training_routes.training_bp)
    app.register_blueprint(session_routes.session_bp)
    app.register_blueprint(reports_routes.reports_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'Zero Trust Security Framework API'}, 200
    
    return app
