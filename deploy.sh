#!/bin/bash

# Zero Trust Security Framework - Deployment Script
# This script automates the deployment process for both frontend and backend

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main deployment function
deploy() {
    local target=$1
    
    print_header "Zero Trust Security Framework Deployment"
    
    # Check prerequisites
    print_info "Checking prerequisites..."
    
    if ! command_exists node; then
        print_error "Node.js is not installed"
        exit 1
    fi
    print_success "Node.js installed"
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 installed"
    
    # Deploy based on target
    case $target in
        frontend)
            deploy_frontend
            ;;
        backend)
            deploy_backend
            ;;
        all)
            deploy_frontend
            deploy_backend
            ;;
        *)
            print_error "Invalid target: $target"
            echo "Usage: ./deploy.sh [frontend|backend|all]"
            exit 1
            ;;
    esac
    
    print_header "Deployment Complete!"
}

deploy_frontend() {
    print_header "Deploying Frontend"
    
    cd frontend
    
    # Check if .env.production exists
    if [ ! -f .env.production ]; then
        print_error ".env.production file not found"
        print_info "Please create .env.production with required variables"
        exit 1
    fi
    
    # Install dependencies
    print_info "Installing dependencies..."
    npm install
    print_success "Dependencies installed"
    
    # Run tests
    print_info "Running tests..."
    npm run test:ci || print_error "Tests failed (continuing anyway)"
    
    # Build production bundle
    print_info "Building production bundle..."
    npm run build:prod
    print_success "Build complete"
    
    # Deploy based on platform
    if command_exists vercel; then
        print_info "Deploying to Vercel..."
        vercel --prod
        print_success "Deployed to Vercel"
    elif command_exists firebase; then
        print_info "Deploying to Firebase Hosting..."
        firebase deploy --only hosting
        print_success "Deployed to Firebase Hosting"
    else
        print_error "No deployment tool found (vercel or firebase)"
        print_info "Install with: npm install -g vercel OR npm install -g firebase-tools"
        exit 1
    fi
    
    cd ..
}

deploy_backend() {
    print_header "Deploying Backend"
    
    cd backend
    
    # Check if .env.production exists
    if [ ! -f .env.production ]; then
        print_error ".env.production file not found"
        print_info "Please create .env.production with required variables"
        exit 1
    fi
    
    # Check if firebase credentials exist
    if [ ! -f firebase-credentials.json ]; then
        print_error "firebase-credentials.json not found"
        print_info "Please download from Firebase Console"
        exit 1
    fi
    
    # Install dependencies
    print_info "Installing dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
    
    # Run tests
    print_info "Running tests..."
    pytest || print_error "Tests failed (continuing anyway)"
    
    # Deploy Firestore rules and indexes
    if command_exists firebase; then
        print_info "Deploying Firestore rules and indexes..."
        firebase deploy --only firestore:rules,firestore:indexes
        print_success "Firestore configuration deployed"
    fi
    
    # Deploy based on platform
    if [ -f render.yaml ]; then
        print_info "Deploying to Render..."
        print_info "Push to Git to trigger Render deployment"
        git add .
        git commit -m "Deploy backend" || true
        git push origin main
        print_success "Pushed to Git (Render will auto-deploy)"
    elif command_exists gcloud; then
        print_info "Deploying to Google Cloud Run..."
        gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/zero-trust-backend
        gcloud run deploy zero-trust-backend \
            --image gcr.io/$(gcloud config get-value project)/zero-trust-backend \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
        print_success "Deployed to Cloud Run"
    else
        print_error "No deployment method found"
        print_info "Configure Render or install gcloud CLI"
        exit 1
    fi
    
    cd ..
}

# Run deployment
if [ $# -eq 0 ]; then
    echo "Usage: ./deploy.sh [frontend|backend|all]"
    exit 1
fi

deploy "$1"
