"""
Check Seed Data Script
Verifies if seed data exists in Firestore without modifying anything

Usage:
    python check_seed_data.py
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from firebase_config import initialize_firebase, get_firestore_client


def check_users(db):
    """Check if test users exist"""
    print("\n=== Checking Test Users ===")
    
    test_emails = ['student@test.edu', 'faculty@test.edu', 'admin@test.edu']
    found_count = 0
    
    for email in test_emails:
        users = db.collection('users').where('email', '==', email).limit(1).stream()
        user_exists = False
        for doc in users:
            user_exists = True
            user_data = doc.to_dict()
            print(f"✓ Found user: {email} (Role: {user_data.get('role')})")
            found_count += 1
            break
        
        if not user_exists:
            print(f"✗ User not found: {email}")
    
    return found_count


def check_policies(db):
    """Check if default policies exist"""
    print("\n=== Checking Default Policies ===")
    
    policy_names = [
        'Lab Server Access',
        'Library Database Access',
        'Admin Panel Access',
        'Student Portal Access',
        'Research Data Storage'
    ]
    found_count = 0
    
    for name in policy_names:
        policies = db.collection('policies').where('name', '==', name).limit(1).stream()
        policy_exists = False
        for doc in policies:
            policy_exists = True
            policy_data = doc.to_dict()
            print(f"✓ Found policy: {name} (Priority: {policy_data.get('priority')})")
            found_count += 1
            break
        
        if not policy_exists:
            print(f"✗ Policy not found: {name}")
    
    return found_count


def check_system_config(db):
    """Check if system configuration exists"""
    print("\n=== Checking System Configuration ===")
    
    config_doc = db.collection('systemConfig').document('settings').get()
    
    if config_doc.exists:
        config_data = config_doc.to_dict()
        print(f"✓ System configuration exists")
        print(f"  Session Timeout: {config_data.get('sessionTimeout')} minutes")
        print(f"  Max Login Attempts: {config_data.get('maxLoginAttempts')}")
        print(f"  Log Retention: {config_data.get('logRetentionDays')} days")
        return True
    else:
        print("✗ System configuration not found")
        return False


def check_keyword_categories(db):
    """Check if keyword categories exist"""
    print("\n=== Checking Keyword Categories ===")
    
    categories_doc = db.collection('systemConfig').document('keywordCategories').get()
    
    if categories_doc.exists:
        categories_data = categories_doc.to_dict()
        categories = categories_data.get('categories', {})
        print(f"✓ Keyword categories exist")
        for category, keywords in categories.items():
            print(f"  {category}: {len(keywords)} keywords")
        return True
    else:
        print("✗ Keyword categories not found")
        return False


def check_access_requests(db):
    """Check if sample access requests exist"""
    print("\n=== Checking Sample Access Requests ===")
    
    # Count all access requests
    requests = db.collection('accessRequests').limit(100).stream()
    count = 0
    
    for doc in requests:
        count += 1
    
    if count > 0:
        print(f"✓ Found {count} access request(s)")
        return count
    else:
        print("✗ No access requests found")
        return 0


def get_collection_stats(db):
    """Get statistics for all collections"""
    print("\n=== Collection Statistics ===")
    
    collections = ['users', 'policies', 'systemConfig', 'accessRequests', 'auditLogs', 'notifications']
    
    for collection_name in collections:
        try:
            docs = db.collection(collection_name).limit(1000).stream()
            count = sum(1 for _ in docs)
            print(f"  {collection_name}: {count} document(s)")
        except Exception as e:
            print(f"  {collection_name}: Error - {str(e)}")


def main():
    """Main function to check seed data"""
    print("=" * 60)
    print("Zero Trust Security Framework - Seed Data Check")
    print("=" * 60)
    
    # Initialize Firebase
    print("\nInitializing Firebase...")
    db = initialize_firebase()
    
    if not db:
        print("✗ Failed to initialize Firebase. Please check your credentials.")
        print("  Make sure firebase-credentials.json exists in the backend directory.")
        sys.exit(1)
    
    print("✓ Firebase initialized successfully")
    
    # Check all seed data
    users_count = check_users(db)
    policies_count = check_policies(db)
    config_exists = check_system_config(db)
    categories_exist = check_keyword_categories(db)
    requests_count = check_access_requests(db)
    
    # Get collection statistics
    get_collection_stats(db)
    
    # Summary
    print("\n" + "=" * 60)
    print("Seed Data Check Summary")
    print("=" * 60)
    print(f"Test Users: {users_count}/3 found")
    print(f"Default Policies: {policies_count}/5 found")
    print(f"System Configuration: {'✓' if config_exists else '✗'}")
    print(f"Keyword Categories: {'✓' if categories_exist else '✗'}")
    print(f"Sample Requests: {requests_count} found")
    
    # Determine if seed data is complete
    is_complete = (
        users_count == 3 and
        policies_count == 5 and
        config_exists and
        categories_exist
    )
    
    if is_complete:
        print("\n✓ All seed data is present and complete!")
        print("  You can start testing the system.")
    else:
        print("\n⚠ Seed data is incomplete or missing.")
        print("  Run 'python seed_data.py' to populate the database.")
    
    print("=" * 60)
    
    return is_complete


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
