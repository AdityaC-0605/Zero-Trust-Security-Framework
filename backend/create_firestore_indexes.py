#!/usr/bin/env python3
"""
Helper script to create Firestore indexes via the Firebase Admin SDK
Note: This requires the indexes to be created manually via Firebase Console
or using Firebase CLI. This script provides the index definitions.
"""

import json
import os

def print_index_instructions():
    """Print instructions for creating Firestore indexes"""
    
    indexes = [
        {
            "name": "Notifications - userId + read + timestamp",
            "collection": "notifications",
            "fields": [
                {"field": "userId", "order": "ASCENDING"},
                {"field": "read", "order": "ASCENDING"},
                {"field": "timestamp", "order": "DESCENDING"}
            ],
            "description": "Required for querying unread notifications by user, ordered by timestamp"
        },
        {
            "name": "Notifications - userId + timestamp",
            "collection": "notifications",
            "fields": [
                {"field": "userId", "order": "ASCENDING"},
                {"field": "timestamp", "order": "DESCENDING"}
            ],
            "description": "Required for querying all notifications by user, ordered by timestamp"
        },
        {
            "name": "Access Requests - userId + timestamp",
            "collection": "accessRequests",
            "fields": [
                {"field": "userId", "order": "ASCENDING"},
                {"field": "timestamp", "order": "DESCENDING"}
            ],
            "description": "Required for querying access requests by user, ordered by timestamp"
        },
        {
            "name": "Access Requests - userId + decision + timestamp",
            "collection": "accessRequests",
            "fields": [
                {"field": "userId", "order": "ASCENDING"},
                {"field": "decision", "order": "ASCENDING"},
                {"field": "timestamp", "order": "DESCENDING"}
            ],
            "description": "Required for querying access requests by user and decision, ordered by timestamp"
        }
    ]
    
    print("=" * 80)
    print("FIRESTORE INDEXES REQUIRED")
    print("=" * 80)
    print("\nThe following indexes need to be created in Firebase Console:\n")
    
    for idx, index in enumerate(indexes, 1):
        print(f"\n{idx}. {index['name']}")
        print(f"   Collection: {index['collection']}")
        print(f"   Fields:")
        for field in index['fields']:
            print(f"     - {field['field']}: {field['order']}")
        print(f"   Description: {index['description']}")
    
    print("\n" + "=" * 80)
    print("HOW TO CREATE:")
    print("=" * 80)
    print("\nOption 1: Click the error links in your backend logs")
    print("  - The error messages contain direct links to create each index")
    print("  - Just click the link and Firebase will create it automatically\n")
    
    print("Option 2: Use Firebase CLI")
    print("  firebase deploy --only firestore:indexes\n")
    
    print("Option 3: Manual creation")
    print("  1. Go to: https://console.firebase.google.com/")
    print("  2. Select project: Zero Trust Security Framework")
    print("  3. Go to Firestore Database → Indexes")
    print("  4. Click 'Create Index' and add the fields listed above\n")
    
    print("Note: Index creation can take 5-10 minutes. The app will work")
    print("without them, but queries will be slower and you'll see warnings.\n")

if __name__ == "__main__":
    print_index_instructions()

