#!/bin/bash

# Deploy Firestore indexes
echo "Deploying Firestore indexes..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found"
    echo "Install with: npm install -g firebase-tools"
    exit 1
fi

# Deploy indexes
firebase deploy --only firestore:indexes

echo "✅ Firestore indexes deployed successfully"
echo ""
echo "Note: Index creation can take several minutes."
echo "Check status at: https://console.firebase.google.com/project/zero-trust-security-framework/firestore/indexes"
