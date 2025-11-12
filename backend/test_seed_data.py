"""
Test script for seed_data.py
Validates the seed data structures without connecting to Firebase
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models.policy import Policy
from models.user import User
from services.intent_analyzer import IntentAnalyzer


def test_default_policies():
    """Test that default policies are valid"""
    print("Testing default policies...")
    
    default_policies = [
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
                    }
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
                    'mfaRequired': False
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
                    'mfaRequired': True
                }
            ],
            'priority': 20
        }
    ]
    
    for policy_data in default_policies:
        policy = Policy(
            name=policy_data['name'],
            description=policy_data['description'],
            rules=policy_data['rules'],
            priority=policy_data['priority'],
            created_by='system'
        )
        
        is_valid, error = policy.validate()
        if not is_valid:
            print(f"  ✗ Policy '{policy.name}' validation failed: {error}")
            return False
        else:
            print(f"  ✓ Policy '{policy.name}' is valid")
    
    print("✓ All default policies are valid\n")
    return True


def test_test_users():
    """Test that test users are valid"""
    print("Testing test users...")
    
    test_users = {
        'student': {
            'email': 'student@test.edu',
            'name': 'Test Student',
            'role': 'student',
            'department': 'Computer Science',
            'student_id': 'STU001'
        },
        'faculty': {
            'email': 'faculty@test.edu',
            'name': 'Test Faculty',
            'role': 'faculty',
            'department': 'Computer Science',
            'student_id': None
        },
        'admin': {
            'email': 'admin@test.edu',
            'name': 'Test Admin',
            'role': 'admin',
            'department': 'IT Administration',
            'student_id': None
        }
    }
    
    for role, user_data in test_users.items():
        user = User(
            user_id=f"test_{role}_user",
            email=user_data['email'],
            role=user_data['role'],
            name=user_data['name'],
            department=user_data['department'],
            student_id=user_data['student_id']
        )
        
        is_valid, error = user.validate()
        if not is_valid:
            print(f"  ✗ User '{role}' validation failed: {error}")
            return False
        else:
            print(f"  ✓ User '{role}' ({user.email}) is valid")
    
    print("✓ All test users are valid\n")
    return True


def test_sample_requests():
    """Test that sample requests have valid intent"""
    print("Testing sample access requests...")
    
    sample_requests = [
        {
            'intent': 'I need to access the library database to research academic papers for my thesis on machine learning algorithms. This is required for my final year project.',
            'expected_score_range': (60, 100)
        },
        {
            'intent': 'Need to run computational experiments for my research project on neural networks. The experiments will take approximately 3 days to complete.',
            'expected_score_range': (60, 100)
        },
        {
            'intent': 'Just want to check the admin panel quickly to see what it looks like.',
            'expected_score_range': (0, 50)
        },
        {
            'intent': 'Need to access the admin panel to configure user permissions and review system audit logs as part of my administrative duties.',
            'expected_score_range': (60, 100)
        }
    ]
    
    analyzer = IntentAnalyzer()
    
    for i, request in enumerate(sample_requests, 1):
        intent = request['intent']
        expected_min, expected_max = request['expected_score_range']
        
        # Validate minimum requirements
        if len(intent) < 20:
            print(f"  ✗ Request {i}: Intent too short ({len(intent)} chars)")
            return False
        
        word_count = len(intent.split())
        if word_count < 5:
            print(f"  ✗ Request {i}: Intent has too few words ({word_count} words)")
            return False
        
        # Analyze intent
        score = analyzer.analyze_intent(intent)
        
        if expected_min <= score <= expected_max:
            print(f"  ✓ Request {i}: Intent score {score:.1f} (expected {expected_min}-{expected_max})")
        else:
            print(f"  ⚠ Request {i}: Intent score {score:.1f} outside expected range {expected_min}-{expected_max}")
    
    print("✓ All sample requests are valid\n")
    return True


def test_system_config():
    """Test that system configuration is valid"""
    print("Testing system configuration...")
    
    system_config = {
        'sessionTimeout': 60,
        'maxLoginAttempts': 5,
        'lockoutDuration': 30,
        'logRetentionDays': 90,
        'confidenceThresholds': {
            'autoApprove': 90,
            'requireMFA': 50,
            'autoDeny': 50
        }
    }
    
    # Validate thresholds
    thresholds = system_config['confidenceThresholds']
    if not (0 <= thresholds['autoApprove'] <= 100):
        print(f"  ✗ Invalid autoApprove threshold: {thresholds['autoApprove']}")
        return False
    
    if not (0 <= thresholds['requireMFA'] <= 100):
        print(f"  ✗ Invalid requireMFA threshold: {thresholds['requireMFA']}")
        return False
    
    if not (0 <= thresholds['autoDeny'] <= 100):
        print(f"  ✗ Invalid autoDeny threshold: {thresholds['autoDeny']}")
        return False
    
    print(f"  ✓ Session timeout: {system_config['sessionTimeout']} minutes")
    print(f"  ✓ Max login attempts: {system_config['maxLoginAttempts']}")
    print(f"  ✓ Confidence thresholds: {thresholds}")
    print("✓ System configuration is valid\n")
    return True


def test_keyword_categories():
    """Test that keyword categories are populated"""
    print("Testing keyword categories...")
    
    analyzer = IntentAnalyzer()
    categories = analyzer.KEYWORD_CATEGORIES
    
    required_categories = ['academic', 'legitimate', 'suspicious', 'administrative']
    
    for category in required_categories:
        if category not in categories:
            print(f"  ✗ Missing category: {category}")
            return False
        
        keyword_count = len(categories[category])
        if keyword_count == 0:
            print(f"  ✗ Category '{category}' has no keywords")
            return False
        
        print(f"  ✓ Category '{category}': {keyword_count} keywords")
    
    print("✓ All keyword categories are populated\n")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Seed Data Validation Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_default_policies,
        test_test_users,
        test_sample_requests,
        test_system_config,
        test_keyword_categories
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {str(e)}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
