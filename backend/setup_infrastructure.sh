#!/bin/bash

# Infrastructure Setup Script for Zero Trust AI Innovations
# This script sets up Redis, RabbitMQ, Ganache, IPFS, and installs dependencies

set -e

echo "=========================================="
echo "Zero Trust AI Infrastructure Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PACKAGE_MANAGER="brew"
    echo -e "${GREEN}Detected macOS${NC}"
else
    echo -e "${RED}This script is optimized for macOS. For other systems, please install dependencies manually.${NC}"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is running
service_running() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services list | grep "$1" | grep "started" >/dev/null 2>&1
    fi
}

echo "Step 1: Installing Python dependencies..."
echo "=========================================="
if [ -d "venv" ]; then
    echo "Virtual environment found. Activating..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

echo "Step 2: Installing Redis..."
echo "=========================================="
if command_exists redis-server; then
    echo "Redis already installed"
else
    echo "Installing Redis..."
    brew install redis
fi

if service_running redis; then
    echo "Redis is already running"
else
    echo "Starting Redis..."
    brew services start redis
fi
echo -e "${GREEN}✓ Redis installed and running${NC}"
echo ""

echo "Step 3: Installing RabbitMQ..."
echo "=========================================="
if command_exists rabbitmq-server; then
    echo "RabbitMQ already installed"
else
    echo "Installing RabbitMQ..."
    brew install rabbitmq
fi

if service_running rabbitmq; then
    echo "RabbitMQ is already running"
else
    echo "Starting RabbitMQ..."
    brew services start rabbitmq
fi
echo -e "${GREEN}✓ RabbitMQ installed and running${NC}"
echo ""

echo "Step 4: Installing Node.js and npm (for Ganache and Truffle)..."
echo "=========================================="
if command_exists node; then
    echo "Node.js already installed: $(node --version)"
else
    echo "Installing Node.js..."
    brew install node
fi
echo -e "${GREEN}✓ Node.js installed${NC}"
echo ""

echo "Step 5: Installing Ganache CLI..."
echo "=========================================="
if command_exists ganache; then
    echo "Ganache already installed"
else
    echo "Installing Ganache CLI..."
    npm install -g ganache
fi
echo -e "${GREEN}✓ Ganache installed${NC}"
echo ""

echo "Step 6: Installing Truffle..."
echo "=========================================="
if command_exists truffle; then
    echo "Truffle already installed"
else
    echo "Installing Truffle..."
    npm install -g truffle
fi
echo -e "${GREEN}✓ Truffle installed${NC}"
echo ""

echo "Step 7: Installing IPFS..."
echo "=========================================="
if command_exists ipfs; then
    echo "IPFS already installed"
else
    echo "Installing IPFS..."
    brew install ipfs
fi

# Initialize IPFS if not already initialized
if [ ! -d "$HOME/.ipfs" ]; then
    echo "Initializing IPFS..."
    ipfs init
fi

echo -e "${GREEN}✓ IPFS installed${NC}"
echo ""

echo "Step 8: Downloading ML models and data..."
echo "=========================================="
# Create directories for ML models
mkdir -p ml_models
mkdir -p geoip2

echo "Note: You'll need to download GeoLite2-City.mmdb from MaxMind"
echo "Visit: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
echo -e "${YELLOW}⚠ Manual download required for GeoIP database${NC}"
echo ""

echo "Step 9: Setting up environment variables..."
echo "=========================================="
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please update .env file with your configuration${NC}"
else
    echo ".env file already exists"
fi
echo -e "${GREEN}✓ Environment file ready${NC}"
echo ""

echo "=========================================="
echo "Infrastructure Setup Complete!"
echo "=========================================="
echo ""
echo "Services Status:"
echo "----------------"
redis-cli ping >/dev/null 2>&1 && echo -e "Redis: ${GREEN}✓ Running${NC}" || echo -e "Redis: ${RED}✗ Not running${NC}"
rabbitmqctl status >/dev/null 2>&1 && echo -e "RabbitMQ: ${GREEN}✓ Running${NC}" || echo -e "RabbitMQ: ${RED}✗ Not running${NC}"
echo ""

echo "Next Steps:"
echo "----------"
echo "1. Update .env file with your API keys (Claude, IP reputation services)"
echo "2. Download GeoLite2-City.mmdb and place in geoip2/ directory"
echo "3. Start Ganache: ganache --port 8545 --networkId 1337"
echo "4. Deploy smart contracts: truffle migrate --network development"
echo "5. Start IPFS daemon: ipfs daemon"
echo "6. Start Celery worker: celery -A celery_config.celery_app worker --loglevel=info"
echo "7. Start Celery beat: celery -A celery_config.celery_app beat --loglevel=info"
echo "8. Start Flask app: python run.py"
echo ""
echo -e "${GREEN}Setup complete! 🚀${NC}"
