"""
Test script for Policy Engine
Tests the core functionality without requiring Firebase connection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from datetime import datetime


# Mock Firestore client for testing
class MockFirestoreClient:
    def __init__(self):
        self.collections_data = {
            'policies': [
                {
                    'policyId': 'policy1',
                    'name': 'Lab Server Access',
                    'description': 'Access policy for lab servers',
                    'rules': [
                        {
                            'resourceType': 'lab_server',
                            'allowedRoles': ['faculty', 'admin'],
                            'minConfidence': 70,
                            'mfaRequired': True,
                            'timeRestrictions': {
                                'startHour': 6,
                                'endHour': 22
                            }
                        }
                    ],
                    'priority': 10,
                    'isActive': True,
                    'createdBy': 'admin1',
                    'createdAt': datetime.utcnow(),
                    'lastModified': datetime.utcnow(),
                    'modifiedBy': 'admin1'
                },
                {
                    'policyId': 'policy2',
                    'name': 'Library Database Access',
                    'description': 'Access policy for library databases',
                    'rules': [
                        {
                            'resourceType': 'library_database',
                            'allowedRoles': ['student', 'faculty', 'admin'],
                            'minConfidence': 60,
                            'mfaRequired': False
                        }
                    ],
                    'priority': 5,
                    'isActive': True,
                    'createdBy': 'admin1',
                    'createdAt': datetime.utcnow(),
                    'lastModified': datetime.utcnow(),
                    'modifiedBy': 'admin1'
                }
            ],
            'accessRequests': []
        }
    
    def collection(self, name):
        return MockCollection(self.collections_data.get(name, []))


class MockCollection:
    def __init__(self, data):
        self.data = data
    
    def where(self, field, op, value):
        filtered = []
        for item in self.data:
            if self._check_condition(item, field, op, value):
                filtered.append(item)
        return MockQuery(filtered)
    
    def _check_condition(self, item, field, op, value):
        if op == '==':
            return item.get(field) == value
        return False
    
    def limit(self, count):
        return MockQuery(self.data[:count])
    
    def stream(self):
        return [MockDocument(item) for item in self.data]


class MockQuery:
    def __init__(self, data):
        self.data = data
    
    def limit(self, count):
        return MockQuery(self.data[:count])
    
    def stream(self):
        return [MockDocument(item) for item in self.data]


class MockDocument:
    def __init__(self, data):
        self.data = data
        self.id = data.get('policyId', 'doc_id')
    
    def to_dict(self):
        return self.data


def test_policy_engine():
    """Test policy engine functionality"""
    
    # Import after mocking
    from services.policy_engine import PolicyEngine
    
    # Create policy engine with mock database
    engine = PolicyEngine()
    engine.db = MockFirestoreClient()
    
    print("=" * 60)
    print("Testing Policy Engine")
    print("=" * 60)
    
    # Test 1: Match policies for faculty accessing lab server
    print("\n1. Testing policy matching for faculty + lab_server:")
    policies = engine.match_policies('lab_server', 'faculty')
    print(f"   Found {len(policies)} matching policies")
    if policies:
        print(f"   Primary policy: {policies[0]['name']}")
        print(f"   ✓ PASS")
    else:
        print(f"   ✗ FAIL: No policies found")
    
    # Test 2: Match policies for student accessing library database
    print("\n2. Testing policy matching for student + library_database:")
    policies = engine.match_policies('library_database', 'student')
    print(f"   Found {len(policies)} matching policies")
    if policies:
        print(f"   Primary policy: {policies[0]['name']}")
        print(f"   ✓ PASS")
    else:
        print(f"   ✗ FAIL: No policies found")
    
    # Test 3: Check role match
    print("\n3. Testing role match validation:")
    score = engine.check_role_match('faculty', 'lab_server')
    print(f"   Role match score: {score}")
    if score == 100:
        print(f"   ✓ PASS: Perfect role match")
    else:
        print(f"   ✗ FAIL: Expected 100, got {score}")
    
    # Test 4: Analyze intent clarity
    print("\n4. Testing intent analysis:")
    good_intent = "I need to access the lab server to run machine learning experiments for my research project on neural networks"
    bad_intent = "urgent need quick access"
    
    good_score = engine._analyze_intent_clarity(good_intent)
    bad_score = engine._analyze_intent_clarity(bad_intent)
    
    print(f"   Good intent score: {good_score}")
    print(f"   Bad intent score: {bad_score}")
    
    if good_score > bad_score and good_score > 60:
        print(f"   ✓ PASS: Intent analysis working correctly")
    else:
        print(f"   ✗ FAIL: Intent analysis not working as expected")
    
    # Test 5: Validate context
    print("\n5. Testing context validation:")
    request_data = {
        'requestedResource': 'lab_server',
        'userRole': 'faculty',
        'timestamp': datetime.utcnow().replace(hour=10),  # 10 AM (within allowed hours)
        'deviceInfo': {'userAgent': 'Mozilla/5.0'},
        'ipAddress': '192.168.1.1'
    }
    
    context_score = engine.validate_context(request_data)
    print(f"   Context validity score: {context_score}")
    
    if context_score >= 80:
        print(f"   ✓ PASS: Context validation working")
    else:
        print(f"   ✗ FAIL: Expected high score, got {context_score}")
    
    # Test 6: Calculate confidence score
    print("\n6. Testing confidence score calculation:")
    request_data = {
        'userId': 'user123',
        'userRole': 'faculty',
        'requestedResource': 'lab_server',
        'intent': 'I need to access the lab server to run machine learning experiments for my research project',
        'duration': '7 days',
        'urgency': 'medium',
        'timestamp': datetime.utcnow(),
        'ipAddress': '192.168.1.1',
        'deviceInfo': {'userAgent': 'Mozilla/5.0'}
    }
    
    score, breakdown = engine.calculate_confidence_score(request_data, [])
    print(f"   Overall confidence score: {score}")
    print(f"   Breakdown:")
    for key, value in breakdown.items():
        print(f"     - {key}: {value}")
    
    if 0 <= score <= 100:
        print(f"   ✓ PASS: Confidence score in valid range")
    else:
        print(f"   ✗ FAIL: Score out of range")
    
    # Test 7: Make decision
    print("\n7. Testing decision making:")
    
    # High confidence - should auto-approve
    high_conf_policy = {
        'policyId': 'policy1',
        'name': 'Test Policy',
        'rules': [{'minConfidence': 70, 'mfaRequired': False}]
    }
    
    decision = engine.make_decision(95, high_conf_policy, breakdown)
    print(f"   High confidence (95) decision: {decision['decision']}")
    if decision['decision'] == 'granted':
        print(f"   ✓ PASS: Auto-approved high confidence")
    else:
        print(f"   ✗ FAIL: Should auto-approve")
    
    # Medium confidence - should require MFA
    decision = engine.make_decision(70, high_conf_policy, breakdown)
    print(f"   Medium confidence (70) decision: {decision['decision']}")
    if decision['decision'] == 'granted_with_mfa':
        print(f"   ✓ PASS: Requires MFA for medium confidence")
    else:
        print(f"   ✗ FAIL: Should require MFA")
    
    # Low confidence - should deny
    decision = engine.make_decision(30, high_conf_policy, breakdown)
    print(f"   Low confidence (30) decision: {decision['decision']}")
    if decision['decision'] == 'denied':
        print(f"   ✓ PASS: Denied low confidence")
    else:
        print(f"   ✗ FAIL: Should deny")
    
    # Test 8: Full evaluation
    print("\n8. Testing full request evaluation:")
    result = engine.evaluate_request(request_data)
    
    print(f"   Decision: {result['decision']}")
    print(f"   Confidence: {result['confidenceScore']}")
    print(f"   Message: {result['message']}")
    print(f"   Policies applied: {len(result['policiesApplied'])}")
    
    if result['decision'] in ['granted', 'granted_with_mfa', 'denied']:
        print(f"   ✓ PASS: Full evaluation completed")
    else:
        print(f"   ✗ FAIL: Invalid decision")
    
    print("\n" + "=" * 60)
    print("Policy Engine Tests Completed")
    print("=" * 60)


def test_policy_model():
    """Test Policy model functionality"""
    from models.policy import Policy
    
    print("\n" + "=" * 60)
    print("Testing Policy Model")
    print("=" * 60)
    
    # Test 1: Create valid policy
    print("\n1. Testing policy creation:")
    try:
        policy = Policy(
            name="Test Policy",
            description="Test policy description",
            rules=[
                {
                    'resourceType': 'test_resource',
                    'allowedRoles': ['student', 'faculty'],
                    'minConfidence': 70,
                    'mfaRequired': True
                }
            ],
            priority=5,
            created_by='admin1'
        )
        print(f"   Created policy: {policy.name}")
        print(f"   ✓ PASS")
    except Exception as e:
        print(f"   ✗ FAIL: {str(e)}")
    
    # Test 2: Validate policy
    print("\n2. Testing policy validation:")
    is_valid, error = policy.validate()
    if is_valid:
        print(f"   ✓ PASS: Policy is valid")
    else:
        print(f"   ✗ FAIL: {error}")
    
    # Test 3: Convert to dict
    print("\n3. Testing policy serialization:")
    policy_dict = policy.to_dict()
    if 'policyId' in policy_dict and 'name' in policy_dict and 'rules' in policy_dict:
        print(f"   ✓ PASS: Policy serialized correctly")
    else:
        print(f"   ✗ FAIL: Missing required fields")
    
    # Test 4: Create from dict
    print("\n4. Testing policy deserialization:")
    policy2 = Policy.from_dict(policy_dict)
    if policy2.name == policy.name and policy2.priority == policy.priority:
        print(f"   ✓ PASS: Policy deserialized correctly")
    else:
        print(f"   ✗ FAIL: Data mismatch")
    
    # Test 5: Invalid policy (no rules)
    print("\n5. Testing invalid policy validation:")
    try:
        invalid_policy = Policy(
            name="Invalid Policy",
            description="No rules",
            rules=[],
            priority=1
        )
        is_valid, error = invalid_policy.validate()
        if not is_valid:
            print(f"   ✓ PASS: Correctly rejected policy with no rules")
        else:
            print(f"   ✗ FAIL: Should reject policy with no rules")
    except Exception as e:
        print(f"   ✓ PASS: Exception raised for invalid policy")
    
    # Test 6: Invalid confidence threshold
    print("\n6. Testing invalid confidence threshold:")
    invalid_rule_policy = Policy(
        name="Invalid Rule Policy",
        description="Invalid confidence",
        rules=[
            {
                'resourceType': 'test',
                'allowedRoles': ['student'],
                'minConfidence': 150  # Invalid: > 100
            }
        ],
        priority=1
    )
    is_valid, error = invalid_rule_policy.validate()
    if not is_valid and 'minConfidence' in error:
        print(f"   ✓ PASS: Correctly rejected invalid confidence threshold")
    else:
        print(f"   ✗ FAIL: Should reject invalid confidence")
    
    print("\n" + "=" * 60)
    print("Policy Model Tests Completed")
    print("=" * 60)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("POLICY ENGINE AND MODEL TEST SUITE")
    print("=" * 60)
    
    try:
        test_policy_model()
        test_policy_engine()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
    
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
