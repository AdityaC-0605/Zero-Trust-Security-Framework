#!/usr/bin/env python3
"""
Create Test User in Firebase
This script creates the test user in Firebase Authentication
"""

import os
import sys
import json
from datetime import datetime

def create_test_user():
    """Create the test user in Firebase Authentication"""
    
    try:
        # Initialize Firebase Admin SDK
        import firebase_admin
        from firebase_admin import credentials, auth, firestore
        
        # Check if already initialized
        try:
            firebase_admin.get_app()
            print("✅ Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            cred_path = './firebase-credentials.json'
            if not os.path.exists(cred_path):
                print(f"❌ Firebase credentials not found at {cred_path}")
                return False
                
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized")
        
        # Test user credentials
        email = "test@example.com"
        password = "Test123!"
        name = "Test User"
        
        print(f"👤 Creating user: {email}")
        
        # Check if user already exists
        try:
            existing_user = auth.get_user_by_email(email)
            print(f"✅ User already exists: {existing_user.uid}")
            print(f"   Email: {existing_user.email}")
            print(f"   Name: {existing_user.display_name}")
            return True
        except auth.UserNotFoundError:
            # User doesn't exist, create it
            pass
        
        # Create the user
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name,
            email_verified=True  # Skip email verification for test user
        )
        
        print(f"✅ User created successfully!")
        print(f"   UID: {user.uid}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.display_name}")
        
        # Create user document in Firestore
        db = firestore.client()
        user_doc = {
            'uid': user.uid,
            'email': user.email,
            'name': user.display_name or name,
            'role': 'admin',  # Make test user an admin
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow(),
            'email_verified': True
        }
        
        db.collection('users').document(user.uid).set(user_doc)
        print(f"✅ User document created in Firestore")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Creating Test User for Zero Trust Framework")
    print("=" * 50)
    
    success = create_test_user()
    
    if success:
        print("\n🎉 Test user created successfully!")
        print("\n📝 Login Credentials:")
        print("   Email: test@example.com")
        print("   Password: Test123!")
        print("\n🔗 You can now login at: http://localhost:3000")
    else:
        print("\n❌ Failed to create test user")
        print("\n💡 Try running the frontend signup instead:")
        print("   1. Go to http://localhost:3000/signup")
        print("   2. Create an account with any email/password")
        print("   3. The system will handle Firebase registration automatically")

if __name__ == "__main__":
    main()