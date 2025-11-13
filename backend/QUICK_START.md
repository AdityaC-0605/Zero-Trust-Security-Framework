# Quick Start Guide - Zero Trust AI Infrastructure

## Prerequisites Check

```bash
# Check if you have the basics
python3 --version  # Should be 3.9+
node --version     # Should be 16+
npm --version
```

## One-Command Setup (macOS)

```bash
cd backend
./setup_infrastructure.sh
```

This will install:
- Redis
- RabbitMQ  
- Ganache
- IPFS
- All Python dependencies
- All Node.js tools

## Configuration

1. **Update .env file:**
```bash
nano .env
```

Add your API keys:
```env
CLAUDE_API_KEY=your_claude_api_key_here
ABUSEIPDB_API_KEY=your_key_here
IPQUALITYSCORE_API_KEY=your_key_here
```

2. **Download GeoIP Database:**
- Visit: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
- Download: GeoLite2-City.mmdb
- Place in: `backend/geoip2/GeoLite2-City.mmdb`

## Start Services

```bash
# Start all infrastructure services
./start_services.sh

# Deploy smart contracts
truffle migrate --network development

# Update .env with contract address from deployment output
```

## Start Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm start
```

## Verify Everything Works

```bash
cd backend
./check_infrastructure.sh
python verify_installation.py
```

## Stop Services

```bash
cd backend
./stop_services.sh
```

## Common Commands

```bash
# Check Redis
redis-cli ping

# Check RabbitMQ
rabbitmqctl status

# Check Celery workers
celery -A celery_config.celery_app inspect active

# View logs
tail -f logs/celery-worker.log
tail -f logs/ganache.log
tail -f logs/ipfs.log

# Restart a service
brew services restart redis
brew services restart rabbitmq
```

## Enable AI Features

Edit `.env` and set to `true`:
```env
BEHAVIORAL_TRACKING_ENABLED=true
THREAT_PREDICTION_ENABLED=true
CONTEXT_EVALUATION_ENABLED=true
SECURITY_ASSISTANT_ENABLED=true
BLOCKCHAIN_ENABLED=true
```

Edit `frontend/.env`:
```env
REACT_APP_BEHAVIORAL_TRACKING_ENABLED=true
REACT_APP_NETWORK_VISUALIZER_ENABLED=true
REACT_APP_SECURITY_ASSISTANT_ENABLED=true
```

## Troubleshooting

**Services won't start?**
```bash
# Check what's running
brew services list

# Restart everything
brew services restart redis
brew services restart rabbitmq
```

**Python packages missing?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Blockchain not working?**
```bash
# Kill and restart Ganache
pkill -f ganache
ganache --port 8545 --networkId 1337 --deterministic
```

## Next Steps

1. ✅ Infrastructure is ready
2. ➡️ Implement Task 2: Behavioral Biometrics
3. ➡️ Continue with remaining AI features

## Need Help?

- Full docs: `INFRASTRUCTURE_SETUP.md`
- Installation summary: `INSTALLATION_SUMMARY.md`
- Check status: `./check_infrastructure.sh`
