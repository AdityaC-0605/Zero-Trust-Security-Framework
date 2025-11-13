# Real-Time Infrastructure Documentation

This document describes the real-time infrastructure components for the Zero Trust AI Innovations platform.

## Overview

The real-time infrastructure consists of three main components:

1. **WebSocket Server** - Real-time bidirectional communication
2. **Redis Caching Layer** - High-performance caching and session management
3. **Celery Background Jobs** - Asynchronous task processing

## 1. WebSocket Server

### Configuration

The WebSocket server is configured in `websocket_config.py` and uses Flask-SocketIO with eventlet for async support.

**Features:**
- Supports 500+ concurrent connections
- Room-based messaging for user-specific updates
- Automatic reconnection with exponential backoff
- Connection tracking and health monitoring

### Event Types

**Client → Server:**
- `connect` - Initial connection
- `join_user_room` - Join user-specific room
- `join_admin_room` - Join admin room (admins only)
- `subscribe_risk_score` - Subscribe to risk score updates
- `subscribe_network_topology` - Subscribe to network topology updates
- `behavioral_data` - Send behavioral tracking data
- `ping` - Connection health check

**Server → Client:**
- `connection_response` - Connection confirmation
- `room_joined` - Room join confirmation
- `risk_score_update` - Real-time risk score updates
- `network_topology_update` - Network topology changes
- `threat_alert` - Threat detection alerts
- `admin_notification` - Admin notifications
- `session_terminated` - Session termination notice
- `policy_update` - Policy change notifications
- `notification` - General notifications
- `pong` - Ping response

### Usage Example (Frontend)

```javascript
import websocketClient from './utils/websocketClient';

// Connect to WebSocket server
websocketClient.connect(
  'http://localhost:5000',
  userId,
  sessionId
);

// Subscribe to risk score updates
websocketClient.subscribeToRiskScore(userId, sessionId);

// Listen for risk score updates
websocketClient.on('risk_score_update', (data) => {
  console.log('Risk score:', data.risk_score);
  updateUI(data);
});

// Send behavioral data
websocketClient.sendBehavioralData({
  keystrokes: [...],
  mouseMovements: [...],
  clicks: [...]
});
```

### Starting the WebSocket Server

The WebSocket server starts automatically with the Flask application:

```bash
python run.py
```

## 2. Redis Caching Layer

### Configuration

Redis is configured in `redis_config.py` with connection pooling and automatic reconnection.

**Default Settings:**
- Host: localhost
- Port: 6379
- DB: 0

### Cache TTLs

Different data types have different TTLs:

- **Behavioral Models**: 1 hour (3600s)
- **Context Scores**: 5 minutes (300s)
- **Threat Predictions**: 30 minutes (1800s)
- **Session Data**: 1 hour (3600s)
- **Device Profiles**: 2 hours (7200s)
- **Policy Performance**: 30 minutes (1800s)

### Cache Service API

The `CacheService` class in `app/services/cache_service.py` provides a unified interface:

```python
from app.services.cache_service import cache_service

# Cache behavioral model
cache_service.cache_behavioral_model(user_id, model_data)

# Get cached model
model = cache_service.get_behavioral_model(user_id)

# Cache contextual score
cache_service.cache_contextual_score(request_id, context_data)

# Cache session data
cache_service.cache_active_session(session_id, session_data)
```

### Starting Redis

```bash
# macOS with Homebrew
brew services start redis

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

## 3. Celery Background Jobs

### Configuration

Celery is configured in `celery_config.py` with RabbitMQ as the message broker and Redis as the result backend.

**Default Settings:**
- Broker: amqp://guest:guest@localhost:5672//
- Backend: redis://localhost:6379/1

### Task Queues

Tasks are routed to different queues:

- `ml_queue` - ML model training and updates
- `blockchain_queue` - Blockchain operations
- `policy_queue` - Policy optimization
- `default` - General tasks

### Scheduled Tasks

**Every 30 seconds:**
- Monitor active sessions for behavioral risk

**Every hour:**
- Cleanup expired sessions
- Run threat detections
- Check blockchain health
- Check policy health

**Every 6 hours:**
- Generate threat predictions
- Cleanup cache

**Daily:**
- Train behavioral models (2 AM)
- Optimize policies (3 AM)
- Calculate prediction accuracy (4 AM)
- Cleanup old notifications (5 AM)
- Generate system health report (6 AM)

**Weekly:**
- Update threat models (Sunday 1 AM)
- Cleanup old behavioral data (Monday 1 AM)
- Cleanup old threat predictions (Tuesday 1 AM)
- Cleanup old ML models (Wednesday 1 AM)

**Monthly:**
- Cleanup old blockchain records (1st at 2 AM)

### Task Types

**ML Tasks** (`app/tasks/ml_tasks.py`):
- `train_behavioral_models` - Train user behavioral models
- `update_threat_models` - Update threat prediction models
- `train_user_behavioral_model` - Train specific user model
- `update_behavioral_baseline` - Update user baseline
- `cleanup_old_models` - Clean up old model versions

**Policy Tasks** (`app/tasks/policy_tasks.py`):
- `optimize_policies` - Optimize all policies
- `calculate_policy_effectiveness` - Calculate policy metrics
- `track_policy_outcome` - Track policy application outcome
- `simulate_policy_change` - Simulate policy changes
- `rollback_policy` - Rollback policy to previous version
- `check_policy_health` - Check policy health

**Blockchain Tasks** (`app/tasks/blockchain_tasks.py`):
- `record_audit_event` - Record event to blockchain
- `sync_audit_trail` - Sync pending events
- `verify_audit_integrity` - Verify audit record integrity
- `batch_record_events` - Batch record multiple events
- `store_large_data_ipfs` - Store large data on IPFS
- `check_blockchain_health` - Check blockchain connectivity
- `cleanup_old_blockchain_records` - Archive old records

**Session Monitoring Tasks** (`app/tasks/session_monitoring_tasks.py`):
- `monitor_active_sessions` - Monitor all active sessions
- `check_session_risk` - Check specific session risk

**Threat Prediction Tasks** (`app/tasks/threat_prediction_tasks.py`):
- `generate_threat_predictions` - Generate threat predictions
- `run_threat_detections` - Run detection algorithms
- `calculate_prediction_accuracy` - Calculate model accuracy

**Cleanup Tasks** (`app/tasks/cleanup_tasks.py`):
- `cleanup_expired_sessions` - Clean up expired sessions
- `cleanup_old_behavioral_data` - Clean up old behavioral data
- `cleanup_old_threat_predictions` - Clean up old predictions
- `cleanup_old_notifications` - Clean up old notifications
- `cleanup_cache` - Clean up expired cache entries
- `generate_system_health_report` - Generate health report

### Starting Celery

**Option 1: Combined Worker and Beat**
```bash
./start_celery.sh
```

**Option 2: Separate Worker and Beat**
```bash
# Terminal 1: Start worker
celery -A celery_config.celery_app worker --loglevel=info --concurrency=4

# Terminal 2: Start beat scheduler
celery -A celery_config.celery_app beat --loglevel=info
```

### Monitoring Celery

```bash
# Monitor tasks
celery -A celery_config.celery_app events

# Inspect active tasks
celery -A celery_config.celery_app inspect active

# Inspect scheduled tasks
celery -A celery_config.celery_app inspect scheduled

# Inspect registered tasks
celery -A celery_config.celery_app inspect registered
```

## Prerequisites

### Install RabbitMQ

**macOS:**
```bash
brew install rabbitmq
brew services start rabbitmq
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
```

**Docker:**
```bash
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management
```

### Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:latest
```

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Install Frontend Dependencies

```bash
cd frontend
npm install socket.io-client
```

## Environment Variables

Add these to your `.env` file:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# WebSocket Configuration
WEBSOCKET_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Starting the Complete System

1. **Start Redis:**
   ```bash
   brew services start redis  # macOS
   # or
   sudo systemctl start redis  # Linux
   ```

2. **Start RabbitMQ:**
   ```bash
   brew services start rabbitmq  # macOS
   # or
   sudo systemctl start rabbitmq-server  # Linux
   ```

3. **Start Celery Worker:**
   ```bash
   cd backend
   ./start_celery.sh
   ```

4. **Start Flask Application (with WebSocket):**
   ```bash
   cd backend
   python run.py
   ```

5. **Start Frontend:**
   ```bash
   cd frontend
   npm start
   ```

## Performance Considerations

### WebSocket
- Supports 500+ concurrent connections
- Uses eventlet for async I/O
- Room-based messaging reduces broadcast overhead
- Automatic reconnection prevents connection loss

### Redis
- In-memory caching for sub-millisecond access
- Connection pooling for efficiency
- Automatic TTL expiration
- Persistence disabled for maximum performance (can be enabled)

### Celery
- Multiple worker processes for parallelism
- Task routing to specialized queues
- Rate limiting to prevent overload
- Automatic retry on failure

## Monitoring and Debugging

### WebSocket Stats
```python
from websocket_config import get_websocket_stats

stats = get_websocket_stats()
print(f"Active connections: {stats['total_connections']}")
print(f"Unique users: {stats['unique_users']}")
```

### Redis Stats
```python
from app.services.cache_service import cache_service

stats = cache_service.get_cache_stats()
print(f"Total keys: {stats['total_keys']}")
print(f"Memory used: {stats['used_memory']}")
```

### Celery Monitoring
```bash
# Flower - Web-based monitoring tool
pip install flower
celery -A celery_config.celery_app flower
# Open http://localhost:5555
```

## Troubleshooting

### WebSocket Connection Issues
- Check CORS configuration in `websocket_config.py`
- Verify Flask app is running with SocketIO
- Check browser console for connection errors
- Ensure firewall allows WebSocket connections

### Redis Connection Issues
- Verify Redis is running: `redis-cli ping`
- Check Redis host and port in `.env`
- Check Redis logs: `tail -f /usr/local/var/log/redis.log`

### Celery Task Issues
- Check RabbitMQ is running: `rabbitmqctl status`
- Verify Celery worker is running
- Check Celery logs for errors
- Inspect task queue: `celery -A celery_config.celery_app inspect active`

## Security Considerations

1. **WebSocket Authentication**: Implement token-based authentication for WebSocket connections
2. **Redis Security**: Use password authentication in production
3. **RabbitMQ Security**: Change default credentials in production
4. **Rate Limiting**: Implement rate limiting for WebSocket events
5. **Input Validation**: Validate all data received via WebSocket

## Production Deployment

### Scaling WebSocket
- Use Redis adapter for multi-server WebSocket
- Deploy behind load balancer with sticky sessions
- Use separate WebSocket server instances

### Scaling Redis
- Use Redis Cluster for horizontal scaling
- Enable persistence for data durability
- Use Redis Sentinel for high availability

### Scaling Celery
- Deploy multiple worker instances
- Use separate workers for different queues
- Monitor queue lengths and scale accordingly

## References

- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.org/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
