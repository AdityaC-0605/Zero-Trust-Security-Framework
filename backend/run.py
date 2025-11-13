from app import create_app
import os

app = create_app()

# Get SocketIO instance if available
socketio = app.config.get('SOCKETIO')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Run with SocketIO if available, otherwise standard Flask
    if socketio:
        print(f"Starting server with WebSocket support on {host}:{port}")
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    else:
        print(f"Starting server without WebSocket support on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
