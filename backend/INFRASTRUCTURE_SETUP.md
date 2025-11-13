# Zero Trust AI Innovations - Infrastructure Setup Guide

This guide covers the setup and configuration of all infrastructure components required for the AI-powered Zero Trust Security Framework.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Component Details](#component-details)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

## Overview

The Zero Trust AI Innovations feature set requires the following infrastructure components:

- **Redis**: Caching layer for ML models, sessions, and real-time data
- **RabbitMQ**: Message queue for background ML jobs and async processing
- **Ganache**: Local Ethereum blockchain for development
- **IPFS**: Distributed storage for large audit data
- **Celery**: Distributed task queue for ML training and predictions
- **WebSocket Server**: Real-time updates for behavioral risk scores
- **ML Libraries**: TensorFlow, PyTorch, scikit-learn for AI models
- **Claude API**: Conversational AI assistant

## Prerequisites

### System Requirements

- **Operating System**: macOS (recommended), Linux, or Windows with WSL2
- **Python**: 3.9 or higher
- **Node.js**: 16.x or higher
- **Memory**: Minimum 8GB RAM (16GB recommended for ML training)
- **Storage**: 10GB free space for ML models and blockchain data

### Required Accounts

1. **Anthropic Claude API**: Sign up at https://console.anthropic.com/
2. **MaxMind GeoIP2**: Register at https://www.maxmind.com/en/geolite2/signup
3. **IP Reputation APIs** (optional):
   - AbuseIPDB: https://www.abuseipdb.com/
   - IPQualityScore: https://www.ipqualityscore.com/

## Quick Start

### Automated Setup (macOS)

```bash
# Navigate to backend directory
cd backend

# Run setup script
./setup_infrastructure.sh

# Update .env file with your API keys
nano .env

# Start all services
./start_services.sh

# Deploy smart contracts
truffle migrate --network development

# Start Flask application
python run.py
```

### Manual Setup

#### 1. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

#### 2. Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Verify:**
```bash
redis-cli ping
# Should return: PONG
```

#### 3. Install RabbitMQ

**macOS:**
```bash
brew install rabbitmq
brew services start rabbitmq
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

**Verify:**
```bash
rabbitmqctl status
```

#### 4. Install Node.js and Blockchain Tools

```bash
# Install Node.js (if not already installed)
# macOS:
brew install node

# Install Ganache CLI
npm install -g ganache

# Install Truffle
npm install -g truffle

# Start Ganache
ganache --port 8545 --networkId 1337 --deterministic
```

#### 5. Install IPFS

**macOS:**
```bash
brew install ipfs
ipfs init
ipfs daemon
```

**Linux:**
```bash
wget https://dist.ipfs.io/go-ipfs/v0.17.0/go-ipfs_v0.17.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.17.0_linux-amd64.tar.gz
cd go-ipfs
sudo bash install.sh
ipfs init
ipfs daemon
```

#### 6. Download GeoIP Database

1. Register at https://www.maxmind.com/en/geolite2/signup
2. Download GeoLite2-City.mmdb
3. Place in `backend/geoip2/` directory

```bash
mkdir -p geoip2
# Copy downloaded file to geoip2/GeoLite2-City.mmdb
```

## Component Details

### Redis Configuration

Redis is used for:
- ML model caching (1-hour TTL)
- Session storage
- Contextual scores (5-minute TTL)
- Threat predictions (30-minute TTL)
- Behavioral profiles (1-hour TTL)

**Configuration file**: `redis.conf`

**Key settings**:
- Port: 6379
- Max memory: 256MB
- Eviction policy: allkeys-lru

### RabbitMQ Configuration

RabbitMQ handles:
- ML model training jobs
- Threat prediction generation
- Policy optimization
- Blockchain event recording

**Queues**:
- `ml_queue`: ML training and inference tasks
- `blockchain_queue`: Blockchain operations
- `policy_queue`: Policy optimization tasks
- `default`: General background tasks

### Celery Configuration

Celery workers process background tasks:

**Start worker**:
```bash
celery -A celery_config.celery_app worker --loglevel=info --concurrency=4
```

**Start beat scheduler**:
```bash
celery -A celery_config.celery_app beat --loglevel=info
```

**Scheduled tasks**:
- Train behavioral models: Daily at 2 AM
- Generate threat predictions: Every 6 hours
- Optimize policies: Daily at 3 AM
- Cleanup sessions: Every hour
- Update threat models: Weekly on Sunday at 1 AM
- Sync blockchain: Every 5 minutes

### Blockchain (Ganache + Truffle)

**Start Ganache**:
```bash
ganache --port 8545 --networkId 1337 --deterministic
```

**Deploy smart contracts**:
```bash
truffle compile
truffle migrate --network development
```

**Get contract address**:
After deployment, update `.env` with the contract address:
```
BLOCKCHAIN_CONTRACT_ADDRESS=0x...
```

### IPFS Configuration

IPFS stores large audit data:

**Start daemon**:
```bash
ipfs daemon
```

**Configuration**:
- Host: localhost
- Port: 5001
- Protocol: http

### WebSocket Server

WebSocket server provides real-time updates:

**Features**:
- Risk score streaming
- Network topology updates
- Threat alerts
- Session notifications

**Configuration**: `websocket_config.py`

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required variables**:

```env
# Claude API
CLAUDE_API_KEY=your_claude_api_key_here

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Blockchain
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
BLOCKCHAIN_CONTRACT_ADDRESS=0x...

# IPFS
IPFS_HOST=localhost
IPFS_PORT=5001

# GeoIP
GEOIP2_DATABASE_PATH=./geoip2/GeoLite2-City.mmdb

# Optional: IP Reputation APIs
ABUSEIPDB_API_KEY=your_key
IPQUALITYSCORE_API_KEY=your_key
```

## Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs
tail -f /usr/local/var/log/redis.log  # macOS
tail -f /var/log/redis/redis-server.log  # Linux

# Restart Redis
brew services restart redis  # macOS
sudo systemctl restart redis  # Linux
```

### RabbitMQ Connection Issues

```bash
# Check RabbitMQ status
rabbitmqctl status

# Check RabbitMQ logs
tail -f /usr/local/var/log/rabbitmq/rabbit@localhost.log  # macOS

# Restart RabbitMQ
brew services restart rabbitmq  # macOS
sudo systemctl restart rabbitmq-server  # Linux
```

### Ganache Connection Issues

```bash
# Check if Ganache is running
curl http://localhost:8545

# Restart Ganache
pkill -f ganache
ganache --port 8545 --networkId 1337 --deterministic
```

### IPFS Connection Issues

```bash
# Check IPFS daemon
ipfs id

# Restart IPFS
pkill -f "ipfs daemon"
ipfs daemon
```

### Celery Worker Issues

```bash
# Check worker status
celery -A celery_config.celery_app inspect active

# Check worker logs
tail -f logs/celery-worker.log

# Restart worker
pkill -f "celery.*worker"
celery -A celery_config.celery_app worker --loglevel=info
```

## Production Deployment

### Redis Production Setup

```bash
# Use Redis Cluster for high availability
# Configure persistence (AOF + RDB)
# Set up replication
# Enable authentication
```

### RabbitMQ Production Setup

```bash
# Use RabbitMQ Cluster
# Configure SSL/TLS
# Set up monitoring
# Enable authentication
```

### Blockchain Production Setup

- Use a private Ethereum network or testnet
- Configure proper gas limits
- Set up monitoring and alerting
- Implement backup strategies

### IPFS Production Setup

- Use IPFS Cluster for redundancy
- Configure pinning services
- Set up gateway access
- Implement access controls

### Scaling Considerations

1. **Horizontal Scaling**:
   - Multiple Celery workers
   - Redis Cluster
   - RabbitMQ Cluster
   - Load-balanced Flask instances

2. **Vertical Scaling**:
   - GPU instances for ML training
   - High-memory instances for Redis
   - SSD storage for blockchain data

3. **Monitoring**:
   - Prometheus + Grafana for metrics
   - ELK Stack for logs
   - Sentry for error tracking

## Service Management

### Start All Services

```bash
./start_services.sh
```

### Stop All Services

```bash
./stop_services.sh
```

### Check Service Status

```bash
# Redis
redis-cli ping

# RabbitMQ
rabbitmqctl status

# Ganache
curl http://localhost:8545

# IPFS
ipfs id

# Celery
celery -A celery_config.celery_app inspect active
```

## Next Steps

After infrastructure setup:

1. Deploy smart contracts: `truffle migrate --network development`
2. Start Flask application: `python run.py`
3. Install frontend dependencies: `cd ../frontend && npm install`
4. Start frontend: `npm start`
5. Access application at http://localhost:3000

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages in console
- Consult component-specific documentation
- Check GitHub issues

## License

This infrastructure setup is part of the Zero Trust AI Innovations project.
