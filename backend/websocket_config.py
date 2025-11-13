"""
WebSocket Configuration for Real-Time Updates
Handles behavioral risk scores, network topology, and notifications
Supports 500+ concurrent connections with room-based messaging
"""

import os
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask import request
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = None

# Track active connections
active_connections = {}

def init_socketio(app):
    """
    Initialize SocketIO with Flask app
    Configured for high concurrency (500+ users)
    """
    global socketio
    
    cors_origins = os.getenv('WEBSOCKET_CORS_ALLOWED_ORIGINS', 'http://localhost:3000')
    
    socketio = SocketIO(
        app,
        cors_allowed_origins=cors_origins.split(','),
        async_mode='eventlet',
        logger=True,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25,
        max_http_buffer_size=1e8,
        transports=['websocket', 'polling'],
        # Performance settings for 500+ concurrent connections
        async_handlers=True,
        manage_session=False,
        # Connection pooling
        client_manager=None,  # Use default in-memory manager
    )
    
    # Register event handlers
    register_handlers(socketio)
    
    logger.info("WebSocket server initialized successfully")
    
    return socketio


def register_handlers(socketio):
    """Register WebSocket event handlers with automatic reconnection support"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection with connection tracking"""
        sid = request.sid
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Track connection
        active_connections[sid] = {
            'connected_at': datetime.utcnow().isoformat(),
            'user_agent': user_agent,
            'rooms': [],
            'user_id': None
        }
        
        logger.info(f'Client connected: {sid} (Total: {len(active_connections)})')
        
        emit('connection_response', {
            'status': 'connected',
            'sid': sid,
            'timestamp': datetime.utcnow().isoformat(),
            'server_time': datetime.utcnow().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection and cleanup"""
        sid = request.sid
        
        # Remove from tracking
        if sid in active_connections:
            user_id = active_connections[sid].get('user_id')
            del active_connections[sid]
            logger.info(f'Client disconnected: {sid} (User: {user_id}, Remaining: {len(active_connections)})')
        else:
            logger.info(f'Client disconnected: {sid}')
    
    @socketio.on('join_user_room')
    def handle_join_user_room(data):
        """Join user-specific room for personalized updates"""
        user_id = data.get('user_id')
        sid = request.sid
        
        if user_id:
            room = f'user_{user_id}'
            join_room(room)
            
            # Track room membership
            if sid in active_connections:
                active_connections[sid]['user_id'] = user_id
                if room not in active_connections[sid]['rooms']:
                    active_connections[sid]['rooms'].append(room)
            
            emit('room_joined', {
                'room': room,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'User {user_id} joined room {room}')
    
    @socketio.on('leave_user_room')
    def handle_leave_user_room(data):
        """Leave user-specific room"""
        user_id = data.get('user_id')
        sid = request.sid
        
        if user_id:
            room = f'user_{user_id}'
            leave_room(room)
            
            # Update room tracking
            if sid in active_connections and room in active_connections[sid]['rooms']:
                active_connections[sid]['rooms'].remove(room)
            
            emit('room_left', {
                'room': room,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'User {user_id} left room {room}')
    
    @socketio.on('join_admin_room')
    def handle_join_admin_room(data):
        """Join admin room for system-wide updates"""
        user_id = data.get('user_id')
        role = data.get('role')
        sid = request.sid
        
        if role == 'admin':
            room = 'admin_room'
            join_room(room)
            
            # Track room membership
            if sid in active_connections:
                if room not in active_connections[sid]['rooms']:
                    active_connections[sid]['rooms'].append(room)
            
            emit('room_joined', {
                'room': room,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'Admin {user_id} joined admin room')
    
    @socketio.on('subscribe_risk_score')
    def handle_subscribe_risk_score(data):
        """Subscribe to real-time risk score updates"""
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        sid = request.sid
        
        if user_id and session_id:
            room = f'risk_score_{session_id}'
            join_room(room)
            
            # Track room membership
            if sid in active_connections:
                if room not in active_connections[sid]['rooms']:
                    active_connections[sid]['rooms'].append(room)
            
            emit('subscribed', {
                'type': 'risk_score',
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'Subscribed to risk score for session {session_id}')
    
    @socketio.on('subscribe_network_topology')
    def handle_subscribe_network_topology(data):
        """Subscribe to network topology updates"""
        user_id = data.get('user_id')
        sid = request.sid
        
        if user_id:
            room = 'network_topology'
            join_room(room)
            
            # Track room membership
            if sid in active_connections:
                if room not in active_connections[sid]['rooms']:
                    active_connections[sid]['rooms'].append(room)
            
            emit('subscribed', {
                'type': 'network_topology',
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f'User {user_id} subscribed to network topology')
    
    @socketio.on('behavioral_data')
    def handle_behavioral_data(data):
        """Receive behavioral tracking data from client"""
        from app.models.behavioral_session import BehavioralSession
        from app.services.audit_logger import log_audit_event
        
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        behavioral_data = data.get('data')
        metadata = data.get('metadata', {})
        
        if user_id and session_id and behavioral_data:
            try:
                # Get or create behavioral session
                session = BehavioralSession.get_by_session_id(session_id)
                
                if not session:
                    # Create new session
                    session = BehavioralSession.create_session(
                        session_id=session_id,
                        user_id=user_id,
                        keystroke_data=behavioral_data.get('keystrokes', []),
                        mouse_data=behavioral_data.get('mouseMovements', []),
                        click_data=behavioral_data.get('clicks', []),
                        scroll_data=behavioral_data.get('scrolls', []),
                        navigation_data=behavioral_data.get('navigation', []),
                        metadata=metadata
                    )
                else:
                    # Append to existing session
                    session.append_behavioral_data(
                        keystroke_data=behavioral_data.get('keystrokes'),
                        mouse_data=behavioral_data.get('mouseMovements'),
                        click_data=behavioral_data.get('clicks'),
                        scroll_data=behavioral_data.get('scrolls'),
                        navigation_data=behavioral_data.get('navigation')
                    )
                
                # Emit acknowledgment
                emit('behavioral_data_received', {
                    'user_id': user_id,
                    'session_id': session_id,
                    'timestamp': data.get('timestamp'),
                    'data_points': session.get_activity_count()
                })
                
                print(f'Received and stored behavioral data for user {user_id}')
                
                # Calculate risk score if enough data
                if session.get_activity_count() >= 50:
                    from app.services.behavioral_biometrics import behavioral_service
                    
                    risk_data = behavioral_service.calculate_risk_score(user_id, session)
                    
                    # Update session with risk score
                    if risk_data.get('baseline_available'):
                        session.update_risk_score(risk_data['risk_score'])
                        
                        # Emit risk score update to user's room
                        emit_risk_score_update(
                            session_id=session_id,
                            risk_score=risk_data['risk_score'],
                            risk_level=risk_data['risk_level'],
                            details=risk_data.get('component_scores'),
                            user_id=user_id
                        )
                
                # Log audit event
                log_audit_event(
                    user_id=user_id,
                    action='behavioral_data_captured',
                    resource_type='behavioral_session',
                    resource_id=str(session_id),
                    details={
                        'keystroke_count': len(behavioral_data.get('keystrokes', [])),
                        'mouse_movement_count': len(behavioral_data.get('mouseMovements', [])),
                        'click_count': len(behavioral_data.get('clicks', [])),
                        'scroll_count': len(behavioral_data.get('scrolls', [])),
                        'navigation_count': len(behavioral_data.get('navigation', []))
                    }
                )
            except Exception as e:
                print(f'Error handling behavioral data: {e}')
                emit('behavioral_data_error', {
                    'error': 'Failed to process behavioral data'
                })
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping for connection health check"""
        emit('pong', {'timestamp': request.args.get('timestamp')})


def emit_risk_score_update(session_id, risk_score, risk_level, details=None, user_id=None):
    """Emit risk score update to subscribed clients"""
    from datetime import datetime
    if socketio:
        # Emit to session-specific room
        room = f'risk_score_{session_id}'
        socketio.emit('risk_score_update', {
            'session_id': session_id,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }, room=room)
        
        # Also emit to user's room for navbar indicator
        if user_id:
            user_room = f'user_{user_id}'
            socketio.emit('risk_score_update', {
                'session_id': session_id,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'details': details,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id
            }, room=user_room)


def emit_network_topology_update(topology_data):
    """Emit network topology update to subscribed clients"""
    if socketio:
        socketio.emit('network_topology_update', topology_data, room='network_topology')


def emit_threat_alert(user_id, threat_data):
    """Emit threat alert to specific user"""
    if socketio:
        room = f'user_{user_id}'
        socketio.emit('threat_alert', threat_data, room=room)


def emit_admin_notification(notification_data):
    """Emit notification to all admins"""
    if socketio:
        socketio.emit('admin_notification', notification_data, room='admin_room')


def emit_session_terminated(user_id, session_id, reason):
    """Emit session termination notification"""
    if socketio:
        room = f'user_{user_id}'
        socketio.emit('session_terminated', {
            'session_id': session_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)


def emit_policy_update(policy_data):
    """Emit policy update notification to all admins"""
    if socketio:
        socketio.emit('policy_update', {
            'policy_id': policy_data.get('policy_id'),
            'change_type': policy_data.get('change_type'),
            'details': policy_data.get('details'),
            'timestamp': datetime.utcnow().isoformat()
        }, room='admin_room')


def emit_notification(user_id, notification_data):
    """Emit notification to specific user"""
    if socketio:
        room = f'user_{user_id}'
        socketio.emit('notification', {
            **notification_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)


def get_websocket_stats():
    """
    Get WebSocket server statistics
    
    Returns:
        dict: Statistics about active connections and rooms
    """
    stats = {
        'total_connections': len(active_connections),
        'connections_by_room': {},
        'active_users': set()
    }
    
    # Count connections per room
    for sid, conn_data in active_connections.items():
        user_id = conn_data.get('user_id')
        if user_id:
            stats['active_users'].add(user_id)
        
        for room in conn_data.get('rooms', []):
            if room not in stats['connections_by_room']:
                stats['connections_by_room'][room] = 0
            stats['connections_by_room'][room] += 1
    
    stats['unique_users'] = len(stats['active_users'])
    stats['active_users'] = list(stats['active_users'])
    
    return stats


def broadcast_to_all(event_name, data):
    """
    Broadcast message to all connected clients
    
    Args:
        event_name: Name of the event
        data: Data to broadcast
    """
    if socketio:
        socketio.emit(event_name, {
            **data,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
