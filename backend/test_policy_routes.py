"""
Test Policy Routes
Simple tests to verify policy configuration endpoints
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.policy import Policy


def test_policy_validation():
    """Test policy validation logic"""
    print("Testing policy validation...")
    
    # Test valid policy
    policy = Policy(
        name="Test Policy",
        description="Test description",
        rules=[
            {
                'resourceType': 'test_resource',
                'allowedRoles': ['student', 'faculty'],
                'minConfidence': 70,
                'mfaRequired': True
            }
        ],
        priority=10,
        created_by='test_admin'
    )
    
    is_valid, error = policy.validate()
    assert is_valid, f"Valid policy failed validation: {error}"
    print("✓ Valid policy passed validation")
    
    # Test invalid policy - no name
    policy_no_name = Policy(
        name="",
        description="Test",
        rules=[{'resourceType': 'test', 'allowedRoles': ['student']}],
        priority=0
    )
    
    is_valid, error = policy_no_name.validate()
    assert not is_valid, "Policy without name should fail validation"
    print("✓ Policy without name correctly failed validation")
    
    # Test invalid policy - no rules
    policy_no_rules = Policy(
        name="Test",
        description="Test",
        rules=[],
        priority=0
    )
    
    is_valid, error = policy_no_rules.validate()
    assert not is_valid, "Policy without rules should fail validation"
    print("✓ Policy without rules correctly failed validation")
    
    # Test invalid confidence threshold
    policy_invalid_confidence = Policy(
        name="Test",
        description="Test",
        rules=[
            {
                'resourceType': 'test',
                'allowedRoles': ['student'],
                'minConfidence': 150  # Invalid - over 100
            }
        ],
        priority=0
    )
    
    is_valid, error = policy_invalid_confidence.validate()
    assert not is_valid, "Policy with invalid confidence should fail validation"
    print("✓ Policy with invalid confidence correctly failed validation")
    
    # Test time restrictions validation
    policy_time_restrictions = Policy(
        name="Test",
        description="Test",
        rules=[
            {
                'resourceType': 'test',
                'allowedRoles': ['student'],
                'minConfidence': 50,
                'timeRestrictions': {
                    'startHour': 6,
                    'endHour': 22,
                    'allowedDays': ['Monday', 'Tuesday', 'Wednesday']
                }
            }
        ],
        priority=0
    )
    
    is_valid, error = policy_time_restrictions.validate()
    assert is_valid, f"Policy with valid time restrictions failed: {error}"
    print("✓ Policy with time restrictions passed validation")
    
    # Test invalid time restrictions
    policy_invalid_time = Policy(
        name="Test",
        description="Test",
        rules=[
            {
                'resourceType': 'test',
                'allowedRoles': ['student'],
                'timeRestrictions': {
                    'startHour': 25  # Invalid - over 23
                }
            }
        ],
        priority=0
    )
    
    is_valid, error = policy_invalid_time.validate()
    assert not is_valid, "Policy with invalid time should fail validation"
    print("✓ Policy with invalid time correctly failed validation")
    
    print("\n✅ All policy validation tests passed!")


def test_policy_to_dict():
    """Test policy serialization"""
    print("\nTesting policy serialization...")
    
    policy = Policy(
        name="Test Policy",
        description="Test description",
        rules=[
            {
                'resourceType': 'test_resource',
                'allowedRoles': ['student'],
                'minConfidence': 60
            }
        ],
        priority=5,
        created_by='admin123'
    )
    
    policy_dict = policy.to_dict()
    
    assert policy_dict['name'] == "Test Policy"
    assert policy_dict['description'] == "Test description"
    assert policy_dict['priority'] == 5
    assert policy_dict['createdBy'] == 'admin123'
    assert len(policy_dict['rules']) == 1
    assert policy_dict['rules'][0]['resourceType'] == 'test_resource'
    
    print("✓ Policy serialization works correctly")
    print("\n✅ All serialization tests passed!")


def test_policy_from_dict():
    """Test policy deserialization"""
    print("\nTesting policy deserialization...")
    
    policy_data = {
        'policyId': 'test123',
        'name': 'Test Policy',
        'description': 'Test description',
        'rules': [
            {
                'resourceType': 'test_resource',
                'allowedRoles': ['faculty'],
                'minConfidence': 80,
                'mfaRequired': True
            }
        ],
        'priority': 15,
        'isActive': True,
        'createdBy': 'admin456'
    }
    
    policy = Policy.from_dict(policy_data)
    
    assert policy.policy_id == 'test123'
    assert policy.name == 'Test Policy'
    assert policy.description == 'Test description'
    assert policy.priority == 15
    assert policy.is_active == True
    assert policy.created_by == 'admin456'
    assert len(policy.rules) == 1
    assert policy.rules[0]['resourceType'] == 'test_resource'
    assert policy.rules[0]['mfaRequired'] == True
    
    print("✓ Policy deserialization works correctly")
    print("\n✅ All deserialization tests passed!")


if __name__ == '__main__':
    print("=" * 60)
    print("Running Policy Routes Tests")
    print("=" * 60)
    
    try:
        test_policy_validation()
        test_policy_to_dict()
        test_policy_from_dict()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
