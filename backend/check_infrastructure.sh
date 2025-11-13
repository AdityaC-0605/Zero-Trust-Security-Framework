#!/bin/bash

# Infrastructure Status Check Script
# Verifies all components are properly installed and running

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Zero Trust AI Infrastructure Status Check"
echo "=========================================="
echo ""

# Function to check if a command exists
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

# Function to check if a service is running
check_service() {
    local service=$1
    local check_command=$2
    
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service is running"
        return 0
    else
        echo -e "${RED}✗${NC} $service is NOT running"
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    if python -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python package '$1' is installed"
        return 0
    else
        echo -e "${RED}✗${NC} Python package '$1' is NOT installed"
        return 1
    fi
}

# Check Python
echo -e "${BLUE}Checking Python...${NC}"
check_command python3
if [ $? -eq 0 ]; then
    python3 --version
fi
echo ""

# Check Virtual Environment
echo -e "${BLUE}Checking Virtual Environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    source venv/bin/activate
    echo "Python: $(which python)"
else
    echo -e "${RED}✗${NC} Virtual environment NOT found"
fi
echo ""

# Check Python Packages
echo -e "${BLUE}Checking Python Packages...${NC}"
check_python_package "flask"
check_python_package "torch"
check_python_package "sklearn"
check_python_package "tensorflow"
check_python_package "redis"
check_python_package "celery"
check_python_package "web3"
check_python_package "ipfshttpclient"
check_python_package "anthropic"
check_python_package "flask_socketio"
echo ""

# Check Node.js
echo -e "${BLUE}Checking Node.js...${NC}"
check_command node
if [ $? -eq 0 ]; then
    node --version
fi
check_command npm
if [ $? -eq 0 ]; then
    npm --version
fi
echo ""

# Check Blockchain Tools
echo -e "${BLUE}Checking Blockchain Tools...${NC}"
check_command ganache
check_command truffle
echo ""

# Check Redis
echo -e "${BLUE}Checking Redis...${NC}"
check_command redis-server
check_service "Redis" "redis-cli ping"
if [ $? -eq 0 ]; then
    echo "Redis version: $(redis-cli --version)"
fi
echo ""

# Check RabbitMQ
echo -e "${BLUE}Checking RabbitMQ...${NC}"
check_command rabbitmq-server
check_service "RabbitMQ" "rabbitmqctl status"
echo ""

# Check IPFS
echo -e "${BLUE}Checking IPFS...${NC}"
check_command ipfs
check_service "IPFS" "ipfs id"
if [ $? -eq 0 ]; then
    echo "IPFS version: $(ipfs version)"
fi
echo ""

# Check Running Services
echo -e "${BLUE}Checking Running Services...${NC}"
check_service "Ganache" "pgrep -f ganache"
check_service "Celery Worker" "pgrep -f 'celery.*worker'"
check_service "Celery Beat" "pgrep -f 'celery.*beat'"
echo ""

# Check Configuration Files
echo -e "${BLUE}Checking Configuration Files...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${RED}✗${NC} .env file NOT found"
fi

if [ -f "redis.conf" ]; then
    echo -e "${GREEN}✓${NC} redis.conf exists"
else
    echo -e "${YELLOW}⚠${NC} redis.conf NOT found (optional)"
fi

if [ -f "truffle-config.js" ]; then
    echo -e "${GREEN}✓${NC} truffle-config.js exists"
else
    echo -e "${RED}✗${NC} truffle-config.js NOT found"
fi

if [ -f "celery_config.py" ]; then
    echo -e "${GREEN}✓${NC} celery_config.py exists"
else
    echo -e "${RED}✗${NC} celery_config.py NOT found"
fi
echo ""

# Check Directories
echo -e "${BLUE}Checking Directories...${NC}"
if [ -d "ml_models" ]; then
    echo -e "${GREEN}✓${NC} ml_models directory exists"
else
    echo -e "${RED}✗${NC} ml_models directory NOT found"
fi

if [ -d "geoip2" ]; then
    echo -e "${GREEN}✓${NC} geoip2 directory exists"
    if [ -f "geoip2/GeoLite2-City.mmdb" ]; then
        echo -e "${GREEN}✓${NC} GeoLite2-City.mmdb exists"
    else
        echo -e "${YELLOW}⚠${NC} GeoLite2-City.mmdb NOT found (download required)"
    fi
else
    echo -e "${RED}✗${NC} geoip2 directory NOT found"
fi

if [ -d "contracts" ]; then
    echo -e "${GREEN}✓${NC} contracts directory exists"
else
    echo -e "${RED}✗${NC} contracts directory NOT found"
fi

if [ -d "logs" ]; then
    echo -e "${GREEN}✓${NC} logs directory exists"
else
    echo -e "${YELLOW}⚠${NC} logs directory NOT found (will be created)"
fi
echo ""

# Check Environment Variables
echo -e "${BLUE}Checking Environment Variables...${NC}"
if [ -f ".env" ]; then
    source .env
    
    if [ -n "$CLAUDE_API_KEY" ]; then
        echo -e "${GREEN}✓${NC} CLAUDE_API_KEY is set"
    else
        echo -e "${YELLOW}⚠${NC} CLAUDE_API_KEY is NOT set"
    fi
    
    if [ -n "$REDIS_URL" ]; then
        echo -e "${GREEN}✓${NC} REDIS_URL is set"
    else
        echo -e "${YELLOW}⚠${NC} REDIS_URL is NOT set"
    fi
    
    if [ -n "$CELERY_BROKER_URL" ]; then
        echo -e "${GREEN}✓${NC} CELERY_BROKER_URL is set"
    else
        echo -e "${YELLOW}⚠${NC} CELERY_BROKER_URL is NOT set"
    fi
fi
echo ""

# Summary
echo "=========================================="
echo "Status Check Complete"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "----------"

if ! command -v redis-server >/dev/null 2>&1; then
    echo "1. Install Redis: brew install redis"
fi

if ! command -v rabbitmq-server >/dev/null 2>&1; then
    echo "2. Install RabbitMQ: brew install rabbitmq"
fi

if ! command -v ganache >/dev/null 2>&1; then
    echo "3. Install Ganache: npm install -g ganache"
fi

if ! command -v ipfs >/dev/null 2>&1; then
    echo "4. Install IPFS: brew install ipfs"
fi

if [ ! -f "geoip2/GeoLite2-City.mmdb" ]; then
    echo "5. Download GeoLite2-City.mmdb from MaxMind"
fi

if [ -z "$CLAUDE_API_KEY" ]; then
    echo "6. Set CLAUDE_API_KEY in .env file"
fi

echo ""
echo "To start all services: ./start_services.sh"
echo "To stop all services: ./stop_services.sh"
