"""
Seed Data Script
Populates the database with default policies, test users, system configuration,
keyword categories, and sample access requests for development and testing.

Usage:
    python seed_data.py

Requirements: 5.1, 11.2
"""

import os
import sys
from datetime import datetime, timedelta
import uuid

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from firebase_config import initialize_firebase, get_firestore_client
from models.policy import Policy
from models.user import User
from services.intent_analyzer import IntentAnalyzer


# Test user credentials for development
TEST_USERS = {
    'student': {
        'email': 'student@test.edu',
        'password': 'Student123!',
        'name': 'Test Student',
        'role': 'student',
        'department': 'Computer Science',
        'student_id': 'STU001'
    },
    'faculty': {
        'email': 'faculty@test.edu',
        'password': 'Faculty123!',
        'name': 'Test Faculty',
        'role': 'faculty',
        'department': 'Computer Science',
        'student_id': None
    },
    'admin': {
        'email': 'admin@test.edu',
        'password': 'Admin123!',
        'name': 'Test Admin',
        'role': 'admin',
        'department': 'IT Administration',
        'student_id': None
    }
}


# Default policies for common resources
DEFAULT_POLICIES = [
    {
        'name': 'Lab Server Access',
        'description': 'Access policy for laboratory servers used for research and coursework',
        'rules': [
            {
                'resourceType': 'lab_server',
                'allowedRoles': ['faculty', 'admin'],
                'minConfidence': 70,
                'mfaRequired': True,
                'timeRestrictions': {
                    'startHour': 6,
                    'endHour': 22,
                    'allowedDays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                },
                'additionalChecks': ['department_match'],
                'rateLimit': '50/hour'
            }
        ],
        'priority': 10
    },
    {
        'name': 'Library Database Access',
        'description': 'Access policy for library databases and research materials',
        'rules': [
            {
                'resourceType': 'library_database',
                'allowedRoles': ['student', 'faculty', 'admin'],
                'minConfidence': 60,
                'mfaRequired': False,
                'rateLimit': '100/hour'
            }
        ],
        'priority': 5
    },
    {
        'name': 'Admin Panel Access',
        'description': 'Access policy for administrative control panel',
        'rules': [
            {
                'resourceType': 'admin_panel',
                'allowedRoles': ['admin'],
                'minConfidence': 90,
                'mfaRequired': True,
                'additionalChecks': ['ip_whitelist'],
                'sessionDuration': 30
            }
        ],
        'priority': 20
    },
    {
        'name': 'Student Portal Access',
        'description': 'Access policy for student information portal',
        'rules': [
            {
                'resourceType': 'student_portal',
                'allowedRoles': ['student', 'faculty', 'admin'],
                'minConfidence': 50,
                'mfaRequired': False,
                'timeRestrictions': {
                    'startHour': 0,
                    'endHour': 23
                }
            }
        ],
        'priority': 3
    },
    {
        'name': 'Research Data Storage',
        'description': 'Access policy for research data storage systems',
        'rules': [
            {
                'resourceType': 'research_storage',
                'allowedRoles': ['faculty', 'admin'],
                'minConfidence': 75,
                'mfaRequired': True,
                'additionalChecks': ['department_match', 'project_authorization']
            }
        ],
        'priority': 15
    }
]


# System configuration with default thresholds and settings
SYSTEM_CONFIG = {
    'mfaRequired': False,  # Global MFA enforcement (can be overridden by policies)
    'sessionTimeout': 60,  # Session timeout in minutes
    'maxLoginAttempts': 5,  # Maximum failed login attempts before lockout
    'lockoutDuration': 30,  # Account lockout duration in minutes
    'logRetentionDays': 90,  # Audit log retention period
    'confidenceThresholds': {
        'autoApprove': 90,  # Auto-approve if confidence >= 90
        'requireMFA': 50,   # Require MFA if confidence between 50-89
        'autoDeny': 50      # Auto-deny if confidence < 50
    },
    'emailNotifications': {
        'enabled': True,
        'alertEmail': 'admin@test.edu',
        'notifyOnHighSeverity': True,
        'notifyOnAccountLockout': True,
        'notifyOnRoleChange': True
    },
    'rateLimits': {
        'accessRequests': '10/hour',
        'apiCalls': '1000/hour',
        'authAttempts': '10/minute'
    },
    'securitySettings': {
        'enforceHttps': True,
        'csrfProtection': True,
        'maxRequestSize': 1048576,  # 1 MB in bytes
        'allowedOrigins': ['http://localhost:3000', 'https://yourdomain.com']
    },
    'notificationSettings': {
        'retentionDays': 30,
        'maxUnreadCount': 100,
        'pushEnabled': True
    },
    'version': '1.0.0',
    'lastUpdated': datetime.utcnow()
}


# Sample access requests for testing different scenarios
SAMPLE_REQUESTS = [
    {
        'user_role': 'student',
        'resource': 'library_database',
        'intent': 'I need to access the library database to research academic papers for my thesis on machine learning algorithms. This is required for my final year project.',
        'duration': '7 days',
        'urgency': 'medium',
        'expected_decision': 'granted'
    },
    {
        'user_role': 'faculty',
        'resource': 'lab_server',
        'intent': 'Need to run computational experiments for my research project on neural networks. The experiments will take approximately 3 days to complete.',
        'duration': '3 days',
        'urgency': 'high',
        'expected_decision': 'granted_with_mfa'
    },
    {
        'user_role': 'student',
        'resource': 'admin_panel',
        'intent': 'Just want to check the admin panel quickly to see what it looks like.',
        'duration': '1 hour',
        'urgency': 'low',
        'expected_decision': 'denied'
    },
    {
        'user_role': 'admin',
        'resource': 'admin_panel',
        'intent': 'Need to access the admin panel to configure user permissions and review system audit logs as part of my administrative duties.',
        'duration': '2 hours',
        'urgency': 'medium',
        'expected_decision': 'granted_with_mfa'
    },
    {
        'user_role': 'student',
        'resource': 'student_portal',
        'intent': 'Accessing student portal to view my grades, course schedule, and register for next semester classes.',
        'duration': '1 hour',
        'urgency': 'low',
        'expected_decision': 'granted'
    },
    {
        'user_role': 'faculty',
        'resource': 'research_storage',
        'intent': 'Need to upload and organize research data from recent experiments. This data will be used for publication in an academic journal.',
        'duration': '14 days',
        'urgency': 'medium',
        'expected_decision': 'granted_with_mfa'
    }
]


def create_test_users(db):
    """
    Create test user accounts for each role
    
    Args:
        db: Firestore client
    
    Returns:
        dict: Dictionary mapping role to user_id
    """
    print("\n=== Creating Test Users ===")
    created_users = {}
    
    for role, user_data in TEST_USERS.items():
        try:
            # Generate a consistent user ID for testing
            user_id = f"test_{role}_user_{uuid.uuid4().hex[:8]}"
            
            # Check if user already exists
            existing_users = db.collection('users').where('email', '==', user_data['email']).limit(1).stream()
            existing_user = None
            for doc in existing_users:
                existing_user = doc
                break
            
            if existing_user:
                print(f"✓ User '{role}' ({user_data['email']}) already exists")
                created_users[role] = existing_user.id
                continue
            
            # Create user object
            user = User(
                user_id=user_id,
                email=user_data['email'],
                role=user_data['role'],
                name=user_data['name'],
                department=user_data['department'],
                student_id=user_data['student_id']
            )
            
            # Validate user
            is_valid, error = user.validate()
            if not is_valid:
                print(f"✗ Failed to create user '{role}': {error}")
                continue
            
            # Save to Firestore
            user_ref = db.collection('users').document(user_id)
            user_ref.set(user.to_dict())
            
            created_users[role] = user_id
            print(f"✓ Created user '{role}' ({user_data['email']})")
            print(f"  User ID: {user_id}")
            print(f"  Password: {user_data['password']}")
        
        except Exception as e:
            print(f"✗ Error creating user '{role}': {str(e)}")
    
    return created_users


def create_default_policies(db):
    """
    Create default policies for common resources
    
    Args:
        db: Firestore client
    
    Returns:
        list: List of created policy IDs
    """
    print("\n=== Creating Default Policies ===")
    created_policies = []
    
    for policy_data in DEFAULT_POLICIES:
        try:
            # Check if policy already exists
            existing = db.collection('policies').where('name', '==', policy_data['name']).limit(1).stream()
            policy_exists = False
            for doc in existing:
                policy_exists = True
                break
            
            if policy_exists:
                print(f"✓ Policy '{policy_data['name']}' already exists")
                continue
            
            # Create policy object
            policy = Policy(
                name=policy_data['name'],
                description=policy_data['description'],
                rules=policy_data['rules'],
                priority=policy_data['priority'],
                created_by='system'
            )
            
            # Validate policy
            is_valid, error = policy.validate()
            if not is_valid:
                print(f"✗ Failed to create policy '{policy_data['name']}': {error}")
                continue
            
            # Save to Firestore
            policy_ref = db.collection('policies').document(policy.policy_id)
            policy_ref.set(policy.to_dict())
            
            created_policies.append(policy.policy_id)
            print(f"✓ Created policy '{policy.name}' (Priority: {policy.priority})")
        
        except Exception as e:
            print(f"✗ Error creating policy '{policy_data['name']}': {str(e)}")
    
    return created_policies


def create_system_configuration(db):
    """
    Create system configuration document with default thresholds and settings
    
    Args:
        db: Firestore client
    
    Returns:
        bool: True if successful
    """
    print("\n=== Creating System Configuration ===")
    
    try:
        # Check if configuration already exists
        config_ref = db.collection('systemConfig').document('settings')
        config_doc = config_ref.get()
        
        if config_doc.exists:
            print("✓ System configuration already exists")
            return True
        
        # Create configuration document
        config_ref.set(SYSTEM_CONFIG)
        print("✓ Created system configuration")
        print(f"  Session Timeout: {SYSTEM_CONFIG['sessionTimeout']} minutes")
        print(f"  Max Login Attempts: {SYSTEM_CONFIG['maxLoginAttempts']}")
        print(f"  Confidence Thresholds: Auto-approve >= {SYSTEM_CONFIG['confidenceThresholds']['autoApprove']}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error creating system configuration: {str(e)}")
        return False


def populate_keyword_categories(db):
    """
    Populate keyword categories for intent analysis
    
    Args:
        db: Firestore client
    
    Returns:
        bool: True if successful
    """
    print("\n=== Populating Keyword Categories ===")
    
    try:
        # Get keyword categories from IntentAnalyzer
        analyzer = IntentAnalyzer()
        keyword_categories = analyzer.KEYWORD_CATEGORIES
        
        # Check if categories already exist
        categories_ref = db.collection('systemConfig').document('keywordCategories')
        categories_doc = categories_ref.get()
        
        if categories_doc.exists:
            print("✓ Keyword categories already exist")
            return True
        
        # Create keyword categories document
        categories_data = {
            'categories': keyword_categories,
            'version': '1.0.0',
            'lastUpdated': datetime.utcnow(),
            'description': 'Keyword categories used for intent analysis in access requests'
        }
        
        categories_ref.set(categories_data)
        
        print("✓ Created keyword categories")
        for category, keywords in keyword_categories.items():
            print(f"  {category}: {len(keywords)} keywords")
        
        return True
    
    except Exception as e:
        print(f"✗ Error populating keyword categories: {str(e)}")
        return False


def create_sample_access_requests(db, user_ids):
    """
    Create sample access requests for testing
    
    Args:
        db: Firestore client
        user_ids (dict): Dictionary mapping role to user_id
    
    Returns:
        list: List of created request IDs
    """
    print("\n=== Creating Sample Access Requests ===")
    created_requests = []
    
    if not user_ids:
        print("✗ No test users available, skipping sample requests")
        return created_requests
    
    for request_data in SAMPLE_REQUESTS:
        try:
            user_role = request_data['user_role']
            
            # Get user ID for this role
            if user_role not in user_ids:
                print(f"✗ No test user found for role '{user_role}', skipping request")
                continue
            
            user_id = user_ids[user_role]
            
            # Create request ID
            request_id = str(uuid.uuid4())
            
            # Create access request document
            access_request = {
                'requestId': request_id,
                'userId': user_id,
                'userRole': user_role,
                'requestedResource': request_data['resource'],
                'intent': request_data['intent'],
                'duration': request_data['duration'],
                'urgency': request_data['urgency'],
                'decision': 'pending',  # Will be evaluated by policy engine
                'confidenceScore': None,
                'confidenceBreakdown': {},
                'policiesApplied': [],
                'timestamp': datetime.utcnow(),
                'ipAddress': '127.0.0.1',
                'deviceInfo': {
                    'userAgent': 'Seed Script',
                    'platform': 'Development',
                    'browser': 'N/A'
                },
                'sessionId': f"seed_session_{uuid.uuid4().hex[:8]}",
                'reviewedBy': None,
                'expiresAt': None,
                'denialReason': None,
                'expectedDecision': request_data['expected_decision']  # For testing reference
            }
            
            # Save to Firestore
            request_ref = db.collection('accessRequests').document(request_id)
            request_ref.set(access_request)
            
            created_requests.append(request_id)
            print(f"✓ Created sample request: {user_role} → {request_data['resource']}")
            print(f"  Expected: {request_data['expected_decision']}")
        
        except Exception as e:
            print(f"✗ Error creating sample request: {str(e)}")
    
    return created_requests


def document_seed_credentials():
    """
    Document seed data credentials for development environment
    
    Returns:
        str: Formatted credentials documentation
    """
    print("\n=== Seed Data Credentials ===")
    
    credentials_doc = """
# Seed Data Credentials

## Test User Accounts

### Student Account
- **Email:** student@test.edu
- **Password:** Student123!
- **Role:** student
- **Department:** Computer Science
- **Student ID:** STU001

### Faculty Account
- **Email:** faculty@test.edu
- **Password:** Faculty123!
- **Role:** faculty
- **Department:** Computer Science

### Admin Account
- **Email:** admin@test.edu
- **Password:** Admin123!
- **Role:** admin
- **Department:** IT Administration

## Default Policies

1. **Lab Server Access** (Priority: 10)
   - Resources: lab_server
   - Allowed Roles: faculty, admin
   - Min Confidence: 70
   - MFA Required: Yes
   - Time Restrictions: 6 AM - 10 PM, Weekdays only

2. **Library Database Access** (Priority: 5)
   - Resources: library_database
   - Allowed Roles: student, faculty, admin
   - Min Confidence: 60
   - MFA Required: No

3. **Admin Panel Access** (Priority: 20)
   - Resources: admin_panel
   - Allowed Roles: admin
   - Min Confidence: 90
   - MFA Required: Yes

4. **Student Portal Access** (Priority: 3)
   - Resources: student_portal
   - Allowed Roles: student, faculty, admin
   - Min Confidence: 50
   - MFA Required: No

5. **Research Data Storage** (Priority: 15)
   - Resources: research_storage
   - Allowed Roles: faculty, admin
   - Min Confidence: 75
   - MFA Required: Yes

## System Configuration

- **Session Timeout:** 60 minutes
- **Max Login Attempts:** 5
- **Lockout Duration:** 30 minutes
- **Log Retention:** 90 days
- **Confidence Thresholds:**
  - Auto-approve: >= 90
  - Require MFA: 50-89
  - Auto-deny: < 50

## Notes

- These credentials are for **DEVELOPMENT ONLY**
- Do NOT use these credentials in production
- Change all passwords before deploying to production
- Firebase Authentication must be configured separately
- Users must be created in Firebase Auth before they can log in

## Sample Access Requests

The seed script creates 6 sample access requests demonstrating:
- Legitimate academic requests (high confidence)
- Role-appropriate requests (medium confidence)
- Suspicious/inappropriate requests (low confidence)
- Various resource types and urgency levels

These requests are in 'pending' status and can be evaluated by the policy engine.
"""
    
    print(credentials_doc)
    
    # Save to file
    try:
        with open('SEED_DATA_CREDENTIALS.md', 'w') as f:
            f.write(credentials_doc)
        print("\n✓ Credentials documented in SEED_DATA_CREDENTIALS.md")
    except Exception as e:
        print(f"\n✗ Error writing credentials file: {str(e)}")
    
    return credentials_doc


def main():
    """Main function to run seed data population"""
    print("=" * 60)
    print("Zero Trust Security Framework - Seed Data Script")
    print("=" * 60)
    
    # Get Firebase client (already initialized by imports)
    print("\nGetting Firebase client...")
    db = get_firestore_client()
    
    if not db:
        print("✗ Failed to get Firebase client. Please check your credentials.")
        print("  Make sure firebase-credentials.json exists in the backend directory.")
        sys.exit(1)
    
    print("✓ Firebase client ready")
    
    # Create test users
    user_ids = create_test_users(db)
    
    # Create default policies
    policy_ids = create_default_policies(db)
    
    # Create system configuration
    create_system_configuration(db)
    
    # Populate keyword categories
    populate_keyword_categories(db)
    
    # Create sample access requests
    request_ids = create_sample_access_requests(db, user_ids)
    
    # Document credentials
    document_seed_credentials()
    
    # Summary
    print("\n" + "=" * 60)
    print("Seed Data Population Complete")
    print("=" * 60)
    print(f"✓ Test Users Created: {len(user_ids)}")
    print(f"✓ Default Policies Created: {len(policy_ids)}")
    print(f"✓ Sample Requests Created: {len(request_ids)}")
    print(f"✓ System Configuration: Created")
    print(f"✓ Keyword Categories: Populated")
    print("\nYou can now use the test accounts to log in and test the system.")
    print("See SEED_DATA_CREDENTIALS.md for detailed credentials and configuration.")
    print("=" * 60)


if __name__ == '__main__':
    main()
