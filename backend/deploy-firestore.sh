#!/bin/bash

# Firestore Security Rules and Indexes Deployment Script
# This script deploys Firestore security rules and indexes to Firebase

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# Function to check if Firebase CLI is installed
check_firebase_cli() {
    if ! command -v firebase &> /dev/null; then
        print_error "Firebase CLI is not installed"
        echo "Install it with: npm install -g firebase-tools"
        exit 1
    fi
    print_success "Firebase CLI is installed"
}

# Function to check if user is logged in
check_firebase_auth() {
    if ! firebase projects:list &> /dev/null; then
        print_error "Not logged in to Firebase"
        echo "Run: firebase login"
        exit 1
    fi
    print_success "Authenticated with Firebase"
}

# Function to validate files exist
check_files() {
    if [ ! -f "firestore.rules" ]; then
        print_error "firestore.rules file not found"
        exit 1
    fi
    
    if [ ! -f "firestore.indexes.json" ]; then
        print_error "firestore.indexes.json file not found"
        exit 1
    fi
    
    print_success "Firestore configuration files found"
}

# Function to validate rules syntax
validate_rules() {
    print_info "Validating security rules syntax..."
    if firebase deploy --only firestore:rules --dry-run &> /dev/null; then
        print_success "Security rules syntax is valid"
    else
        print_error "Security rules syntax validation failed"
        firebase deploy --only firestore:rules --dry-run
        exit 1
    fi
}

# Function to show current project
show_project() {
    PROJECT=$(firebase use)
    print_info "Current Firebase project: ${PROJECT}"
}

# Function to deploy rules
deploy_rules() {
    print_info "Deploying Firestore security rules..."
    if firebase deploy --only firestore:rules; then
        print_success "Security rules deployed successfully"
    else
        print_error "Failed to deploy security rules"
        exit 1
    fi
}

# Function to deploy indexes
deploy_indexes() {
    print_info "Deploying Firestore indexes..."
    if firebase deploy --only firestore:indexes; then
        print_success "Indexes deployment initiated"
        print_warning "Note: Index creation may take 5-10 minutes to complete"
        print_info "Check status at: https://console.firebase.google.com/project/_/firestore/indexes"
    else
        print_error "Failed to deploy indexes"
        exit 1
    fi
}

# Function to show deployment summary
show_summary() {
    echo ""
    echo "=========================================="
    echo "  Deployment Summary"
    echo "=========================================="
    echo ""
    echo "✓ Security Rules: Deployed"
    echo "✓ Indexes: Deployment initiated"
    echo ""
    echo "Collections secured:"
    echo "  • users (read: own/admin, write: admin)"
    echo "  • accessRequests (read: own/admin, write: backend)"
    echo "  • auditLogs (read: admin, write: backend)"
    echo "  • policies (read: all, write: admin)"
    echo "  • systemConfig (read/write: admin)"
    echo "  • notifications (read: own, update: own)"
    echo ""
    echo "Indexes created:"
    echo "  • auditLogs: userId+timestamp, eventType+timestamp, severity+timestamp, result+timestamp"
    echo "  • accessRequests: userId+timestamp, decision+timestamp, userId+decision+timestamp"
    echo "  • notifications: userId+read+timestamp"
    echo "  • policies: isActive+priority"
    echo ""
    echo "Next steps:"
    echo "  1. Verify rules in Firebase Console → Firestore → Rules"
    echo "  2. Wait for indexes to complete (5-10 minutes)"
    echo "  3. Check index status in Firebase Console → Firestore → Indexes"
    echo "  4. Test security rules using the Rules Playground"
    echo ""
    echo "=========================================="
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "  Firestore Deployment Script"
    echo "  Zero Trust Security Framework"
    echo "=========================================="
    echo ""
    
    # Pre-flight checks
    print_info "Running pre-flight checks..."
    check_firebase_cli
    check_firebase_auth
    check_files
    echo ""
    
    # Show current project
    show_project
    echo ""
    
    # Ask for confirmation
    read -p "Deploy to this project? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    echo ""
    
    # Validate rules
    validate_rules
    echo ""
    
    # Deploy
    deploy_rules
    echo ""
    deploy_indexes
    echo ""
    
    # Show summary
    show_summary
}

# Parse command line arguments
case "${1:-}" in
    --rules-only)
        check_firebase_cli
        check_firebase_auth
        check_files
        validate_rules
        deploy_rules
        ;;
    --indexes-only)
        check_firebase_cli
        check_firebase_auth
        check_files
        deploy_indexes
        ;;
    --validate)
        check_files
        validate_rules
        print_success "Validation complete"
        ;;
    --help|-h)
        echo "Usage: ./deploy-firestore.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  (no options)      Deploy both rules and indexes"
        echo "  --rules-only      Deploy only security rules"
        echo "  --indexes-only    Deploy only indexes"
        echo "  --validate        Validate rules syntax without deploying"
        echo "  --help, -h        Show this help message"
        echo ""
        ;;
    *)
        main
        ;;
esac
