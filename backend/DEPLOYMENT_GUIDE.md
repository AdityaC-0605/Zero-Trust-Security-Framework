# Zero Trust AI Innovations - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Zero Trust AI Innovations feature set to production. The system requires specialized infrastructure for ML services, blockchain nodes, real-time processing, and distributed storage.

## Table of Contents

1. [Infrastructure Requirements](#infrastructure-requirements)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [ML Services Deployment](#ml-services-deployment)
5. [Blockchain Node Setup](#blockchain-node-setup)
6. [Redis and Message Queue Configuration](#redis-and-message-queue-configuration)
7. [WebSocket Server Deployment](#websocket-server-deployment)
8. [Frontend Deployment](#frontend-deployment)
9. [Monitoring and Alerting](#monitoring-and-alerting)
10. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
11. [Security Hardening](#security-hardening)
12. [Troubleshooting](#troubleshooting)

---

## Infrastructure Requirements

### Compute Resources

#### Backend API Server
- **CPU**: 4 vCPUs minimum, 8 vCPUs recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 100GB SSD
- **OS**: Ubuntu 22.04 LTS or later
- **Network**: 1 Gbps

#### ML Services Server
- **CPU**: 8 vCPUs minimum
- **GPU**: NVIDIA T4 or better (16GB VRAM minimum)
- **RAM**: 32GB minimum, 64GB recommended
- **Storage**: 200GB SSD (for models and training data)
- **OS**: Ubuntu 22.04 LTS with CUDA 12.0+
- **Network**: 1 Gbps

#### Redis Cache Server
- **CPU**: 2 vCPUs
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1 Gbps

#### Message Queue Server (RabbitMQ/Celery)
- **CPU**: 2 vCPUs
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1 Gbps

#### Blockchain Node
- **CPU**: 4 vCPUs
- **RAM**: 8GB minimum
- **Storage**: 100GB SSD (grows over time)
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1 Gbps


### Storage Requirements

#### Firestore Database
- **Estimated Size**: ~10GB for 10,000 users
- **Growth Rate**: ~1GB per 1,000 additional users
- **Backup**: Daily automated backups
- **Retention**: 30 days

#### IPFS Storage
- **Initial**: 50GB
- **Growth Rate**: ~5GB per month (audit data)
- **Replication**: 3 nodes minimum

#### ML Model Storage
- **Initial**: 5GB (base models)
- **Growth Rate**: ~500MB per month (model updates)
- **Backup**: Version-controlled storage

#### Blockchain Storage
- **Initial**: 20GB
- **Growth Rate**: ~2GB per month
- **Backup**: Full node replication

### Network Requirements

- **Bandwidth**: 100 Mbps minimum, 1 Gbps recommended
- **Latency**: <100ms for behavioral tracking
- **WebSocket Support**: Required for real-time features
- **SSL/TLS**: Required for all external connections
- **Firewall Rules**: 
  - Port 443 (HTTPS)
  - Port 8545 (Ethereum RPC)
  - Port 5001 (IPFS API)
  - Port 6379 (Redis)
  - Port 5672 (RabbitMQ)

---

## Prerequisites

### Software Dependencies

```bash
# System packages
sudo apt-get update
sudo apt-get install -y \
  python3.10 \
  python3-pip \
  python3-venv \
  nodejs \
  npm \
  redis-server \
  rabbitmq-server \
  nginx \
  git \
  curl \
  wget \
  build-essential

# NVIDIA drivers and CUDA (for ML server)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-12-0

# Docker (for containerized services)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Cloud Provider Setup

#### Google Cloud Platform (Recommended)

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create project
gcloud projects create zerotrust-ai-prod --name="Zero Trust AI Production"
gcloud config set project zerotrust-ai-prod

# Enable required APIs
gcloud services enable \
  compute.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  cloudkms.googleapis.com
```

#### AWS Alternative

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
```

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/zero-trust-ai.git
cd zero-trust-ai
```

### 2. Create Environment Files

Create `.env` file in the backend directory:

```bash
# Backend .env
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<generate-secure-random-key>
DEBUG=False

# Firebase Configuration
FIREBASE_PROJECT_ID=zerotrust-ai-prod
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<secure-redis-password>
REDIS_DB=0

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=zerotrust
RABBITMQ_PASSWORD=<secure-rabbitmq-password>

# Celery Configuration
CELERY_BROKER_URL=amqp://zerotrust:<password>@localhost:5672//
CELERY_RESULT_BACKEND=redis://:<password>@localhost:6379/1

# Blockchain Configuration
ETHEREUM_RPC_URL=http://localhost:8545
ETHEREUM_PRIVATE_KEY=<ethereum-private-key>
CONTRACT_ADDRESS=<deployed-contract-address>

# IPFS Configuration
IPFS_API_URL=http://localhost:5001
IPFS_GATEWAY_URL=https://ipfs.io/ipfs/

# Claude API Configuration
CLAUDE_API_KEY=<your-claude-api-key>
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# External APIs
ABUSEIPDB_API_KEY=<your-abuseipdb-key>
IPQUALITYSCORE_API_KEY=<your-ipqs-key>
MAXMIND_LICENSE_KEY=<your-maxmind-key>

# ML Configuration
ML_MODEL_PATH=/opt/zerotrust/ml_models
GPU_ENABLED=true
CUDA_VISIBLE_DEVICES=0

# Security
JWT_SECRET_KEY=<generate-secure-jwt-key>
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=INFO
```

Create `.env` file in the frontend directory:

```bash
# Frontend .env
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:

```bash
REACT_APP_API_URL=https://api.zerotrust.example.com
REACT_APP_WS_URL=wss://api.zerotrust.example.com
REACT_APP_FIREBASE_API_KEY=<firebase-api-key>
REACT_APP_FIREBASE_AUTH_DOMAIN=zerotrust-ai-prod.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=zerotrust-ai-prod
REACT_APP_SENTRY_DSN=<your-sentry-dsn>
```

### 3. Generate Secure Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate Redis password
openssl rand -base64 32

# Generate RabbitMQ password
openssl rand -base64 32
```


---

## ML Services Deployment

### 1. Install ML Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu120

# Install TensorFlow with GPU support
pip install tensorflow[and-cuda]

# Install other ML libraries
pip install -r requirements.txt
```

### 2. Download Pre-trained Models

```bash
# Create model directory
sudo mkdir -p /opt/zerotrust/ml_models
sudo chown $USER:$USER /opt/zerotrust/ml_models

# Download base models
python3 scripts/download_models.py
```

### 3. Configure GPU

```bash
# Verify GPU availability
nvidia-smi

# Test CUDA with PyTorch
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Test TensorFlow GPU
python3 -c "import tensorflow as tf; print(f'GPU devices: {tf.config.list_physical_devices(\"GPU\")}')"
```

### 4. Create ML Service Deployment Script

Create `deploy_ml_services.sh`:

```bash
#!/bin/bash

# ML Services Deployment Script

set -e

echo "Deploying ML Services..."

# Activate virtual environment
source /opt/zerotrust/backend/venv/bin/activate

# Set environment variables
export CUDA_VISIBLE_DEVICES=0
export TF_FORCE_GPU_ALLOW_GROWTH=true

# Start behavioral biometrics service
echo "Starting behavioral biometrics service..."
python3 -m app.services.behavioral_biometrics &
BEHAVIORAL_PID=$!

# Start threat prediction service
echo "Starting threat prediction service..."
python3 -m app.services.threat_predictor &
THREAT_PID=$!

# Start contextual intelligence service
echo "Starting contextual intelligence service..."
python3 -m app.services.contextual_intelligence &
CONTEXT_PID=$!

# Save PIDs
echo $BEHAVIORAL_PID > /var/run/behavioral_service.pid
echo $THREAT_PID > /var/run/threat_service.pid
echo $CONTEXT_PID > /var/run/context_service.pid

echo "ML Services deployed successfully"
echo "Behavioral PID: $BEHAVIORAL_PID"
echo "Threat PID: $THREAT_PID"
echo "Context PID: $CONTEXT_PID"
```

Make it executable:

```bash
chmod +x deploy_ml_services.sh
```

### 5. Create Systemd Service

Create `/etc/systemd/system/zerotrust-ml.service`:

```ini
[Unit]
Description=Zero Trust ML Services
After=network.target

[Service]
Type=forking
User=zerotrust
Group=zerotrust
WorkingDirectory=/opt/zerotrust/backend
Environment="PATH=/opt/zerotrust/backend/venv/bin"
Environment="CUDA_VISIBLE_DEVICES=0"
ExecStart=/opt/zerotrust/backend/deploy_ml_services.sh
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable zerotrust-ml
sudo systemctl start zerotrust-ml
sudo systemctl status zerotrust-ml
```

---

## Blockchain Node Setup

### 1. Install Ethereum Client (Geth)

```bash
# Add Ethereum PPA
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install -y ethereum

# Verify installation
geth version
```

### 2. Initialize Blockchain

For production, you can either:
- Connect to Ethereum mainnet (expensive)
- Use a private Ethereum network (recommended)
- Use a testnet (Sepolia, Goerli)

#### Option A: Private Network (Recommended)

Create genesis file `genesis.json`:

```json
{
  "config": {
    "chainId": 1337,
    "homesteadBlock": 0,
    "eip150Block": 0,
    "eip155Block": 0,
    "eip158Block": 0,
    "byzantiumBlock": 0,
    "constantinopleBlock": 0,
    "petersburgBlock": 0,
    "istanbulBlock": 0
  },
  "difficulty": "0x400",
  "gasLimit": "0x8000000",
  "alloc": {}
}
```

Initialize:

```bash
# Create data directory
sudo mkdir -p /opt/zerotrust/blockchain
sudo chown $USER:$USER /opt/zerotrust/blockchain

# Initialize
geth --datadir /opt/zerotrust/blockchain init genesis.json

# Create account
geth --datadir /opt/zerotrust/blockchain account new
# Save the address and password securely
```

### 3. Start Geth Node

Create systemd service `/etc/systemd/system/geth.service`:

```ini
[Unit]
Description=Ethereum Geth Node
After=network.target

[Service]
Type=simple
User=zerotrust
Group=zerotrust
ExecStart=/usr/bin/geth \
  --datadir /opt/zerotrust/blockchain \
  --networkid 1337 \
  --http \
  --http.addr 127.0.0.1 \
  --http.port 8545 \
  --http.api eth,net,web3,personal \
  --mine \
  --miner.threads 1 \
  --allow-insecure-unlock
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the node:

```bash
sudo systemctl daemon-reload
sudo systemctl enable geth
sudo systemctl start geth
sudo systemctl status geth
```

### 4. Install Truffle and Deploy Smart Contracts

```bash
# Install Truffle globally
sudo npm install -g truffle

# Navigate to backend
cd /opt/zerotrust/backend

# Compile contracts
truffle compile

# Deploy contracts
truffle migrate --network development

# Save contract address
CONTRACT_ADDRESS=$(truffle networks | grep "PolicyEnforcement" | awk '{print $2}')
echo "CONTRACT_ADDRESS=$CONTRACT_ADDRESS" >> .env
```

### 5. Setup IPFS

```bash
# Download IPFS
wget https://dist.ipfs.tech/kubo/v0.24.0/kubo_v0.24.0_linux-amd64.tar.gz
tar -xvzf kubo_v0.24.0_linux-amd64.tar.gz
cd kubo
sudo bash install.sh

# Initialize IPFS
ipfs init

# Configure IPFS
ipfs config Addresses.API /ip4/127.0.0.1/tcp/5001
ipfs config Addresses.Gateway /ip4/127.0.0.1/tcp/8080

# Start IPFS daemon
ipfs daemon &
```

Create systemd service `/etc/systemd/system/ipfs.service`:

```ini
[Unit]
Description=IPFS Daemon
After=network.target

[Service]
Type=simple
User=zerotrust
Group=zerotrust
ExecStart=/usr/local/bin/ipfs daemon
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```


---

## Redis and Message Queue Configuration

### 1. Configure Redis

Edit `/etc/redis/redis.conf`:

```conf
# Bind to localhost only (use private network in production)
bind 127.0.0.1

# Set password
requirepass <your-secure-redis-password>

# Enable persistence
save 900 1
save 300 10
save 60 10000

# Set max memory
maxmemory 8gb
maxmemory-policy allkeys-lru

# Enable AOF
appendonly yes
appendfilename "appendonly.aof"

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

Restart Redis:

```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server
```

Test connection:

```bash
redis-cli -a <your-password> ping
# Should return: PONG
```

### 2. Configure RabbitMQ

```bash
# Start RabbitMQ
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Create user
sudo rabbitmqctl add_user zerotrust <your-secure-password>
sudo rabbitmqctl set_user_tags zerotrust administrator
sudo rabbitmqctl set_permissions -p / zerotrust ".*" ".*" ".*"

# Remove default guest user (security)
sudo rabbitmqctl delete_user guest
```

Access management UI at `http://localhost:15672`

### 3. Configure Celery Workers

Create `celery_config.py`:

```python
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('zerotrust')

celery_app.config_from_object({
    'broker_url': 'amqp://zerotrust:<password>@localhost:5672//',
    'result_backend': 'redis://:<password>@localhost:6379/1',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'worker_prefetch_multiplier': 4,
    'worker_max_tasks_per_child': 1000,
    'task_acks_late': True,
    'task_reject_on_worker_lost': True,
})

# Scheduled tasks
celery_app.conf.beat_schedule = {
    'train-behavioral-models': {
        'task': 'app.tasks.ml_tasks.train_behavioral_models',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'generate-threat-predictions': {
        'task': 'app.tasks.threat_prediction_tasks.generate_predictions',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'optimize-policies': {
        'task': 'app.tasks.policy_tasks.optimize_policies',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'cleanup-old-sessions': {
        'task': 'app.tasks.cleanup_tasks.cleanup_sessions',
        'schedule': crontab(hour=1, minute=0),  # 1 AM daily
    },
}
```

Create systemd service `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target rabbitmq-server.service redis-server.service

[Service]
Type=forking
User=zerotrust
Group=zerotrust
WorkingDirectory=/opt/zerotrust/backend
Environment="PATH=/opt/zerotrust/backend/venv/bin"
ExecStart=/opt/zerotrust/backend/venv/bin/celery -A celery_config.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --logfile=/var/log/celery/worker.log \
  --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create systemd service `/etc/systemd/system/celery-beat.service`:

```ini
[Unit]
Description=Celery Beat Scheduler
After=network.target rabbitmq-server.service redis-server.service

[Service]
Type=simple
User=zerotrust
Group=zerotrust
WorkingDirectory=/opt/zerotrust/backend
Environment="PATH=/opt/zerotrust/backend/venv/bin"
ExecStart=/opt/zerotrust/backend/venv/bin/celery -A celery_config.celery_app beat \
  --loglevel=info \
  --logfile=/var/log/celery/beat.log \
  --pidfile=/var/run/celery/beat.pid
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create log directories:

```bash
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown zerotrust:zerotrust /var/log/celery /var/run/celery
```

Start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
sudo systemctl status celery-worker celery-beat
```

---

## WebSocket Server Deployment

### 1. Configure Flask-SocketIO

The WebSocket server is integrated with the Flask backend. Configure in `app/__init__.py`:

```python
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')

CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)
```

### 2. Install WebSocket Dependencies

```bash
pip install flask-socketio gevent gevent-websocket
```

### 3. Create WebSocket Service

Create systemd service `/etc/systemd/system/zerotrust-websocket.service`:

```ini
[Unit]
Description=Zero Trust WebSocket Server
After=network.target redis-server.service

[Service]
Type=simple
User=zerotrust
Group=zerotrust
WorkingDirectory=/opt/zerotrust/backend
Environment="PATH=/opt/zerotrust/backend/venv/bin"
ExecStart=/opt/zerotrust/backend/venv/bin/python3 websocket_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `websocket_server.py`:

```python
from app import socketio, app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting WebSocket server on port 5001")
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=False,
        use_reloader=False
    )
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable zerotrust-websocket
sudo systemctl start zerotrust-websocket
sudo systemctl status zerotrust-websocket
```

### 4. Configure Nginx for WebSocket

Add to nginx configuration:

```nginx
# WebSocket upgrade
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

upstream websocket_backend {
    server 127.0.0.1:5001;
}

server {
    listen 443 ssl http2;
    server_name api.zerotrust.example.com;

    ssl_certificate /etc/letsencrypt/live/api.zerotrust.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.zerotrust.example.com/privkey.pem;

    # WebSocket location
    location /socket.io/ {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Regular API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```


---

## Frontend Deployment

### 1. Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Output will be in frontend/build/
```

### 2. Deploy to Firebase Hosting (Option A)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Deploy
firebase deploy --only hosting
```

### 3. Deploy to Nginx (Option B)

```bash
# Copy build files
sudo mkdir -p /var/www/zerotrust
sudo cp -r frontend/build/* /var/www/zerotrust/

# Set permissions
sudo chown -R www-data:www-data /var/www/zerotrust
```

Create nginx configuration `/etc/nginx/sites-available/zerotrust-frontend`:

```nginx
server {
    listen 80;
    server_name zerotrust.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name zerotrust.example.com;

    ssl_certificate /etc/letsencrypt/live/zerotrust.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/zerotrust.example.com/privkey.pem;

    root /var/www/zerotrust;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React Router support
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/zerotrust-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Setup SSL Certificates

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d zerotrust.example.com -d api.zerotrust.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Monitoring and Alerting

### 1. Setup Prometheus

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
sudo mv prometheus-2.45.0.linux-amd64 /opt/prometheus
```

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'zerotrust-backend'
    static_configs:
      - targets: ['localhost:5000']
  
  - job_name: 'zerotrust-ml'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
  
  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['localhost:15692']
  
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

Create systemd service:

```bash
sudo systemctl enable prometheus
sudo systemctl start prometheus
```

### 2. Setup Grafana

```bash
# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Access Grafana at `http://localhost:3000` (default: admin/admin)

### 3. Configure Alerting

Create `alerting_rules.yml`:

```yaml
groups:
  - name: zerotrust_alerts
    interval: 30s
    rules:
      - alert: HighRiskScoreDetected
        expr: behavioral_risk_score > 80
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High risk score detected for user {{ $labels.user_id }}"
      
      - alert: ThreatPredictionAccuracyLow
        expr: threat_prediction_accuracy < 0.80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Threat prediction accuracy below 80%"
      
      - alert: BlockchainSyncDelayed
        expr: blockchain_sync_delay_seconds > 3600
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Blockchain sync delayed by more than 1 hour"
      
      - alert: MLModelInferenceSlow
        expr: ml_inference_duration_seconds > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ML model inference taking longer than 3 seconds"
```

### 4. Setup Sentry for Error Tracking

```bash
# Install Sentry SDK in backend
pip install sentry-sdk[flask]

# Install Sentry SDK in frontend
npm install @sentry/react
```

Configure in backend `app/__init__.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment='production'
)
```

Configure in frontend `src/index.js`:

```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [new Sentry.BrowserTracing()],
  tracesSampleRate: 0.1,
  environment: 'production'
});
```


---

## Backup and Disaster Recovery

### 1. Firestore Backup

```bash
# Create backup script
cat > /opt/zerotrust/scripts/backup_firestore.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BUCKET="gs://zerotrust-backups"

gcloud firestore export $BACKUP_BUCKET/firestore-$DATE \
  --project=zerotrust-ai-prod

echo "Firestore backup completed: $DATE"
EOF

chmod +x /opt/zerotrust/scripts/backup_firestore.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /opt/zerotrust/scripts/backup_firestore.sh
```

### 2. ML Models Backup

```bash
# Create backup script
cat > /opt/zerotrust/scripts/backup_models.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/ml_models"
MODEL_DIR="/opt/zerotrust/ml_models"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/models-$DATE.tar.gz -C $MODEL_DIR .

# Keep only last 7 days
find $BACKUP_DIR -name "models-*.tar.gz" -mtime +7 -delete

echo "ML models backup completed: $DATE"
EOF

chmod +x /opt/zerotrust/scripts/backup_models.sh

# Schedule daily backups
# Add to crontab: 0 3 * * * /opt/zerotrust/scripts/backup_models.sh
```

### 3. Blockchain Backup

```bash
# Create backup script
cat > /opt/zerotrust/scripts/backup_blockchain.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/blockchain"
BLOCKCHAIN_DIR="/opt/zerotrust/blockchain"

mkdir -p $BACKUP_DIR

# Stop geth temporarily
systemctl stop geth

# Backup blockchain data
tar -czf $BACKUP_DIR/blockchain-$DATE.tar.gz -C $BLOCKCHAIN_DIR .

# Restart geth
systemctl start geth

# Keep only last 30 days
find $BACKUP_DIR -name "blockchain-*.tar.gz" -mtime +30 -delete

echo "Blockchain backup completed: $DATE"
EOF

chmod +x /opt/zerotrust/scripts/backup_blockchain.sh

# Schedule weekly backups
# Add to crontab: 0 4 * * 0 /opt/zerotrust/scripts/backup_blockchain.sh
```

### 4. Redis Backup

Redis automatically creates RDB snapshots based on configuration. To manually backup:

```bash
# Create backup script
cat > /opt/zerotrust/scripts/backup_redis.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/redis"

mkdir -p $BACKUP_DIR

# Trigger save
redis-cli -a <password> BGSAVE

# Wait for save to complete
while [ $(redis-cli -a <password> LASTSAVE) -eq $(redis-cli -a <password> LASTSAVE) ]; do
  sleep 1
done

# Copy RDB file
cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump-$DATE.rdb

# Keep only last 7 days
find $BACKUP_DIR -name "dump-*.rdb" -mtime +7 -delete

echo "Redis backup completed: $DATE"
EOF

chmod +x /opt/zerotrust/scripts/backup_redis.sh
```

### 5. Disaster Recovery Plan

Create `/opt/zerotrust/docs/disaster_recovery.md`:

```markdown
# Disaster Recovery Plan

## Recovery Time Objective (RTO): 4 hours
## Recovery Point Objective (RPO): 24 hours

### Recovery Steps

1. **Provision New Infrastructure**
   - Spin up new VMs matching specifications
   - Install base software dependencies
   - Configure networking and firewall rules

2. **Restore Firestore**
   ```bash
   gcloud firestore import gs://zerotrust-backups/firestore-YYYYMMDD_HHMMSS
   ```

3. **Restore ML Models**
   ```bash
   tar -xzf /backup/ml_models/models-latest.tar.gz -C /opt/zerotrust/ml_models
   ```

4. **Restore Blockchain**
   ```bash
   systemctl stop geth
   tar -xzf /backup/blockchain/blockchain-latest.tar.gz -C /opt/zerotrust/blockchain
   systemctl start geth
   ```

5. **Restore Redis**
   ```bash
   systemctl stop redis-server
   cp /backup/redis/dump-latest.rdb /var/lib/redis/dump.rdb
   systemctl start redis-server
   ```

6. **Redeploy Services**
   ```bash
   systemctl start zerotrust-ml
   systemctl start celery-worker
   systemctl start celery-beat
   systemctl start zerotrust-websocket
   systemctl start geth
   systemctl start ipfs
   ```

7. **Verify Services**
   - Check all systemd services are running
   - Verify API endpoints respond
   - Test WebSocket connections
   - Verify blockchain sync
   - Test ML model inference

8. **Update DNS**
   - Point DNS to new infrastructure
   - Wait for propagation (up to 48 hours)

### Contact Information
- On-Call Engineer: +1-XXX-XXX-XXXX
- DevOps Lead: devops@zerotrust.example.com
- Security Team: security@zerotrust.example.com
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Install UFW
sudo apt-get install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow internal services (adjust IPs for your network)
sudo ufw allow from 10.0.0.0/8 to any port 6379  # Redis
sudo ufw allow from 10.0.0.0/8 to any port 5672  # RabbitMQ
sudo ufw allow from 10.0.0.0/8 to any port 8545  # Ethereum

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 2. Secure Redis

```bash
# Disable dangerous commands
redis-cli -a <password> CONFIG SET rename-command FLUSHDB ""
redis-cli -a <password> CONFIG SET rename-command FLUSHALL ""
redis-cli -a <password> CONFIG SET rename-command CONFIG ""

# Save configuration
redis-cli -a <password> CONFIG REWRITE
```

### 3. Secure RabbitMQ

```bash
# Disable guest user
sudo rabbitmqctl delete_user guest

# Enable SSL
sudo rabbitmq-plugins enable rabbitmq_auth_mechanism_ssl

# Configure SSL in /etc/rabbitmq/rabbitmq.conf
```

### 4. Secure Nginx

Add to nginx configuration:

```nginx
# Hide nginx version
server_tokens off;

# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20 nodelay;
```

### 5. Setup Fail2Ban

```bash
# Install fail2ban
sudo apt-get install -y fail2ban

# Create jail for nginx
sudo cat > /etc/fail2ban/jail.d/nginx.conf << 'EOF'
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
findtime = 600
bantime = 3600
EOF

# Restart fail2ban
sudo systemctl restart fail2ban
```

### 6. Regular Security Updates

```bash
# Enable automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Configure in /etc/apt/apt.conf.d/50unattended-upgrades
```

---

## Troubleshooting

### Common Issues

#### 1. ML Model Inference Slow

**Symptoms**: API responses taking > 3 seconds

**Solutions**:
```bash
# Check GPU utilization
nvidia-smi

# Check if models are cached
redis-cli -a <password> KEYS "model:*"

# Restart ML services
sudo systemctl restart zerotrust-ml

# Check logs
sudo journalctl -u zerotrust-ml -f
```

#### 2. WebSocket Connection Failures

**Symptoms**: Real-time updates not working

**Solutions**:
```bash
# Check WebSocket service
sudo systemctl status zerotrust-websocket

# Check nginx WebSocket configuration
sudo nginx -t

# Test WebSocket connection
wscat -c wss://api.zerotrust.example.com/socket.io/

# Check logs
sudo tail -f /var/log/nginx/error.log
```

#### 3. Blockchain Sync Issues

**Symptoms**: Audit logs not being recorded

**Solutions**:
```bash
# Check geth status
sudo systemctl status geth

# Check sync status
geth attach /opt/zerotrust/blockchain/geth.ipc
> eth.syncing

# Check logs
sudo journalctl -u geth -f

# Restart geth
sudo systemctl restart geth
```

#### 4. High Memory Usage

**Symptoms**: System running out of memory

**Solutions**:
```bash
# Check memory usage
free -h
htop

# Check Redis memory
redis-cli -a <password> INFO memory

# Adjust Redis maxmemory
redis-cli -a <password> CONFIG SET maxmemory 4gb

# Restart services
sudo systemctl restart redis-server
```

#### 5. Celery Workers Not Processing Tasks

**Symptoms**: Background jobs not executing

**Solutions**:
```bash
# Check worker status
sudo systemctl status celery-worker

# Check RabbitMQ queues
sudo rabbitmqctl list_queues

# Purge stuck tasks
celery -A celery_config.celery_app purge

# Restart workers
sudo systemctl restart celery-worker celery-beat
```

### Log Locations

```
Backend API: /var/log/zerotrust/backend.log
ML Services: /var/log/zerotrust/ml.log
Celery Worker: /var/log/celery/worker.log
Celery Beat: /var/log/celery/beat.log
Nginx Access: /var/log/nginx/access.log
Nginx Error: /var/log/nginx/error.log
Redis: /var/log/redis/redis-server.log
RabbitMQ: /var/log/rabbitmq/
Geth: sudo journalctl -u geth
IPFS: sudo journalctl -u ipfs
```

### Health Check Endpoints

```bash
# Backend API
curl https://api.zerotrust.example.com/health

# ML Services
curl http://localhost:8000/health

# Redis
redis-cli -a <password> ping

# RabbitMQ
curl -u zerotrust:<password> http://localhost:15672/api/healthchecks/node

# Blockchain
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  http://localhost:8545
```

---

## Post-Deployment Checklist

- [ ] All services running and healthy
- [ ] SSL certificates installed and auto-renewal configured
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up
- [ ] Backup scripts scheduled
- [ ] Security hardening applied
- [ ] DNS records updated
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations
- [ ] Documentation updated
- [ ] Runbook created for on-call engineers

---

## Support

For deployment support:
- **DevOps Team**: devops@zerotrust.example.com
- **On-Call**: +1-XXX-XXX-XXXX
- **Documentation**: https://docs.zerotrust.example.com

## License

This deployment guide is proprietary and confidential.
