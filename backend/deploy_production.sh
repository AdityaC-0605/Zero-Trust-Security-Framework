#!/bin/bash

################################################################################
# Zero Trust AI Innovations - Production Deployment Script
# 
# This script automates the deployment of all Zero Trust AI components to
# production infrastructure.
#
# Usage: ./deploy_production.sh [options]
# Options:
#   --skip-ml         Skip ML services deployment
#   --skip-blockchain Skip blockchain deployment
#   --skip-frontend   Skip frontend deployment
#   --dry-run         Show what would be deployed without executing
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_USER="zerotrust"
DEPLOY_GROUP="zerotrust"
INSTALL_DIR="/opt/zerotrust"
LOG_DIR="/var/log/zerotrust"
BACKUP_DIR="/backup/zerotrust"

# Parse command line arguments
SKIP_ML=false
SKIP_BLOCKCHAIN=false
SKIP_FRONTEND=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-ml)
      SKIP_ML=true
      shift
      ;;
    --skip-blockchain)
      SKIP_BLOCKCHAIN=true
      shift
      ;;
    --skip-frontend)
      SKIP_FRONTEND=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

log_info "Starting Zero Trust AI Production Deployment"
log_info "=============================================="

# Step 1: Pre-deployment checks
log_info "Step 1: Running pre-deployment checks..."


# Check required commands
REQUIRED_COMMANDS=("python3" "pip3" "npm" "redis-cli" "systemctl" "nginx")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v $cmd &> /dev/null; then
        log_error "Required command not found: $cmd"
        exit 1
    fi
done

# Check environment file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    log_error ".env file not found in $SCRIPT_DIR"
    exit 1
fi

# Load environment variables
source "$SCRIPT_DIR/.env"

# Verify critical environment variables
REQUIRED_VARS=("FIREBASE_PROJECT_ID" "REDIS_HOST" "RABBITMQ_HOST" "SECRET_KEY")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        log_error "Required environment variable not set: $var"
        exit 1
    fi
done

log_info "Pre-deployment checks passed ✓"

# Step 2: Create deployment user and directories
log_info "Step 2: Setting up deployment user and directories..."

if ! id "$DEPLOY_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$DEPLOY_USER"
    log_info "Created deployment user: $DEPLOY_USER"
fi

# Create directories
mkdir -p "$INSTALL_DIR"/{backend,frontend,ml_models,blockchain,logs}
mkdir -p "$LOG_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p /var/run/celery

# Set permissions
chown -R $DEPLOY_USER:$DEPLOY_GROUP "$INSTALL_DIR"
chown -R $DEPLOY_USER:$DEPLOY_GROUP "$LOG_DIR"
chown -R $DEPLOY_USER:$DEPLOY_GROUP "$BACKUP_DIR"
chown -R $DEPLOY_USER:$DEPLOY_GROUP /var/run/celery

log_info "Directories created and permissions set ✓"

# Step 3: Backup existing installation
log_info "Step 3: Backing up existing installation..."

if [ -d "$INSTALL_DIR/backend" ]; then
    BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
    tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$INSTALL_DIR" . 2>/dev/null || true
    log_info "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
fi

# Step 4: Deploy backend
log_info "Step 4: Deploying backend..."

# Copy backend files
rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
    "$SCRIPT_DIR/" "$INSTALL_DIR/backend/"

# Copy environment file
cp "$SCRIPT_DIR/.env" "$INSTALL_DIR/backend/.env"

# Create virtual environment
cd "$INSTALL_DIR/backend"
if [ ! -d "venv" ]; then
    sudo -u $DEPLOY_USER python3 -m venv venv
fi

# Install dependencies
sudo -u $DEPLOY_USER venv/bin/pip install --upgrade pip
sudo -u $DEPLOY_USER venv/bin/pip install -r requirements.txt

log_info "Backend deployed ✓"

# Step 5: Deploy ML services
if [ "$SKIP_ML" = false ]; then
    log_info "Step 5: Deploying ML services..."
    
    # Install ML dependencies
    sudo -u $DEPLOY_USER venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu120
    sudo -u $DEPLOY_USER venv/bin/pip install tensorflow[and-cuda]
    
    # Download pre-trained models
    if [ -f "$INSTALL_DIR/backend/scripts/download_models.py" ]; then
        sudo -u $DEPLOY_USER venv/bin/python3 scripts/download_models.py
    fi
    
    log_info "ML services deployed ✓"
else
    log_warn "Skipping ML services deployment"
fi

# Step 6: Deploy blockchain node
if [ "$SKIP_BLOCKCHAIN" = false ]; then
    log_info "Step 6: Deploying blockchain node..."
    
    # Initialize blockchain if not exists
    if [ ! -d "$INSTALL_DIR/blockchain/geth" ]; then
        if [ -f "$SCRIPT_DIR/genesis.json" ]; then
            sudo -u $DEPLOY_USER geth --datadir "$INSTALL_DIR/blockchain" init "$SCRIPT_DIR/genesis.json"
        fi
    fi
    
    # Compile and deploy smart contracts
    cd "$INSTALL_DIR/backend"
    if [ -d "contracts" ]; then
        npm install -g truffle
        sudo -u $DEPLOY_USER truffle compile
        # Note: Manual deployment required for production
        log_warn "Smart contracts compiled. Manual deployment required."
    fi
    
    log_info "Blockchain node deployed ✓"
else
    log_warn "Skipping blockchain deployment"
fi

# Step 7: Configure services
log_info "Step 7: Configuring systemd services..."

# Backend API service
cat > /etc/systemd/system/zerotrust-api.service << EOF
[Unit]
Description=Zero Trust API Server
After=network.target redis-server.service

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 run:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# ML services
if [ "$SKIP_ML" = false ]; then
cat > /etc/systemd/system/zerotrust-ml.service << EOF
[Unit]
Description=Zero Trust ML Services
After=network.target

[Service]
Type=forking
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
Environment="CUDA_VISIBLE_DEVICES=0"
ExecStart=$INSTALL_DIR/backend/deploy_ml_services.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

# Celery worker
cat > /etc/systemd/system/celery-worker.service << EOF
[Unit]
Description=Celery Worker
After=network.target rabbitmq-server.service redis-server.service

[Service]
Type=forking
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/celery -A celery_config.celery_app worker --loglevel=info --concurrency=4 --logfile=$LOG_DIR/celery-worker.log --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -TERM \$MAINPID
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery beat
cat > /etc/systemd/system/celery-beat.service << EOF
[Unit]
Description=Celery Beat Scheduler
After=network.target rabbitmq-server.service redis-server.service

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/celery -A celery_config.celery_app beat --loglevel=info --logfile=$LOG_DIR/celery-beat.log --pidfile=/var/run/celery/beat.pid
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# WebSocket server
cat > /etc/systemd/system/zerotrust-websocket.service << EOF
[Unit]
Description=Zero Trust WebSocket Server
After=network.target redis-server.service

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/python3 websocket_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Blockchain node
if [ "$SKIP_BLOCKCHAIN" = false ]; then
cat > /etc/systemd/system/geth.service << EOF
[Unit]
Description=Ethereum Geth Node
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
ExecStart=/usr/bin/geth --datadir $INSTALL_DIR/blockchain --networkid 1337 --http --http.addr 127.0.0.1 --http.port 8545 --http.api eth,net,web3,personal --mine --miner.threads 1 --allow-insecure-unlock
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

# IPFS daemon
if [ "$SKIP_BLOCKCHAIN" = false ]; then
cat > /etc/systemd/system/ipfs.service << EOF
[Unit]
Description=IPFS Daemon
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_GROUP
ExecStart=/usr/local/bin/ipfs daemon
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

log_info "Systemd services configured ✓"

# Step 8: Deploy frontend
if [ "$SKIP_FRONTEND" = false ]; then
    log_info "Step 8: Deploying frontend..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies
    npm install
    
    # Build for production
    npm run build
    
    # Copy to web root
    mkdir -p /var/www/zerotrust
    cp -r build/* /var/www/zerotrust/
    chown -R www-data:www-data /var/www/zerotrust
    
    log_info "Frontend deployed ✓"
else
    log_warn "Skipping frontend deployment"
fi

# Step 9: Configure Nginx
log_info "Step 9: Configuring Nginx..."

cat > /etc/nginx/sites-available/zerotrust << 'EOF'
# API Server
upstream api_backend {
    server 127.0.0.1:5000;
}

# WebSocket Server
upstream websocket_backend {
    server 127.0.0.1:5001;
}

# WebSocket upgrade
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.zerotrust.example.com zerotrust.example.com;
    return 301 https://$server_name$request_uri;
}

# API Server
server {
    listen 443 ssl http2;
    server_name api.zerotrust.example.com;

    ssl_certificate /etc/letsencrypt/live/api.zerotrust.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.zerotrust.example.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

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
        
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}

# Frontend
server {
    listen 443 ssl http2;
    server_name zerotrust.example.com;

    ssl_certificate /etc/letsencrypt/live/zerotrust.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/zerotrust.example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    root /var/www/zerotrust;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

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
EOF

# Enable site
ln -sf /etc/nginx/sites-available/zerotrust /etc/nginx/sites-enabled/
nginx -t

log_info "Nginx configured ✓"

# Step 10: Reload systemd and start services
log_info "Step 10: Starting services..."

if [ "$DRY_RUN" = false ]; then
    systemctl daemon-reload
    
    # Start services
    systemctl enable zerotrust-api
    systemctl start zerotrust-api
    
    if [ "$SKIP_ML" = false ]; then
        systemctl enable zerotrust-ml
        systemctl start zerotrust-ml
    fi
    
    systemctl enable celery-worker celery-beat
    systemctl start celery-worker celery-beat
    
    systemctl enable zerotrust-websocket
    systemctl start zerotrust-websocket
    
    if [ "$SKIP_BLOCKCHAIN" = false ]; then
        systemctl enable geth ipfs
        systemctl start geth ipfs
    fi
    
    # Reload Nginx
    systemctl reload nginx
    
    log_info "All services started ✓"
else
    log_warn "DRY RUN: Services not started"
fi

# Step 11: Verify deployment
log_info "Step 11: Verifying deployment..."

sleep 5  # Give services time to start

# Check service status
SERVICES=("zerotrust-api" "celery-worker" "celery-beat" "zerotrust-websocket")
if [ "$SKIP_ML" = false ]; then
    SERVICES+=("zerotrust-ml")
fi
if [ "$SKIP_BLOCKCHAIN" = false ]; then
    SERVICES+=("geth" "ipfs")
fi

ALL_RUNNING=true
for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet $service; then
        log_info "$service: Running ✓"
    else
        log_error "$service: Not running ✗"
        ALL_RUNNING=false
    fi
done

# Test API endpoint
if curl -f -s http://localhost:5000/health > /dev/null; then
    log_info "API health check: Passed ✓"
else
    log_error "API health check: Failed ✗"
    ALL_RUNNING=false
fi

# Final status
echo ""
log_info "=============================================="
if [ "$ALL_RUNNING" = true ]; then
    log_info "Deployment completed successfully! ✓"
    log_info ""
    log_info "Next steps:"
    log_info "1. Configure SSL certificates with certbot"
    log_info "2. Update DNS records to point to this server"
    log_info "3. Run smoke tests"
    log_info "4. Monitor logs for any issues"
else
    log_error "Deployment completed with errors ✗"
    log_error "Check service logs for details:"
    log_error "  journalctl -u <service-name> -f"
    exit 1
fi
