import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# Firebase Admin SDK initialization
# This will be properly configured once Firebase credentials are available

_firebase_initialized = False
_db = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_initialized, _db
    
    if _firebase_initialized:
        return _db
    
    try:
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
        
        if os.path.exists(cred_path):
            # Check if Firebase is already initialized
            try:
                firebase_admin.get_app()
                # Already initialized, just get the client
                _db = firestore.client()
                _firebase_initialized = True
                print("Firebase already initialized, using existing app")
            except ValueError:
                # Not initialized yet, initialize it
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                _firebase_initialized = True
                print("Firebase initialized successfully")
        else:
            print(f"Warning: Firebase credentials file not found at {cred_path}")
            print("Please download your Firebase service account credentials and place them at the specified path")
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
    
    return _db

def get_firestore_client():
    """Get Firestore client instance"""
    global _db
    if not _firebase_initialized:
        _db = initialize_firebase()
    return _db

def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return None
