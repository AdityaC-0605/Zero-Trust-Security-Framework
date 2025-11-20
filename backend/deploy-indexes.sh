#!/bin/bash

# Deploy Firestore indexes
echo "Deploying Firestore indexes..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found"
    echo "Install with: npm install -g firebase-tools"
    exit 1
fi

# Ensure we're in the backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Check if firebase.json exists
if [ ! -f "firebase.json" ]; then
    echo "❌ firebase.json not found in backend directory"
    exit 1
fi

# Check if firestore.indexes.json exists
if [ ! -f "firestore.indexes.json" ]; then
    echo "❌ firestore.indexes.json not found"
    exit 1
fi

# Deploy indexes
echo "Running: firebase deploy --only firestore:indexes"
firebase deploy --only firestore:indexes

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Firestore indexes deployed successfully"
    echo ""
    echo "Note: Index creation can take several minutes."
    echo "Check status at: https://console.firebase.google.com/project/zero-trust-security-framework/firestore/indexes"
else
    echo ""
    echo "❌ Failed to deploy indexes. Make sure you're logged in: firebase login"
    exit 1
fi
