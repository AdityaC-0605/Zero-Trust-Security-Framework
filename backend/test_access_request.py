"""
Test script for Access Request Model
Tests the core functionality without requiring Firebase connection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from datetime import datetime


def test_access_request_model():
    """Test AccessRequest model functionality"""
    from models.access_request import AccessRequest
    
    print("=" * 60)
    print("Testing Access Request Model")
    print("=" * 60)
    
    # Test 1: Create valid access request
    print("\n1. Testing access request creation:")
    try:
        access_request = AccessRequest(
            user_id='user123',
            user_role='student',
            requested_resource='library_database',
            intent='I need to access the library database to research academic papers for my thesis on machine learning algorithms',
            duration='7 days',
            urgency='medium'
        )
        print(f"   Created request: {access_request.request_id}")
        print(f"   ✓ PASS")
    except Exception as e:
        print(f"   ✗ FAIL: {str(e)}")
        return
    
    # Test 2: Validate valid access request
    print("\n2. Testing access request validation (valid):")
    is_valid, error = access_request.validate()
    if is_valid:
        print(f"   ✓ PASS: Access request is valid")
    else:
        print(f"   ✗ FAIL: {error}")
    
    # Test 3: Convert to dict
    print("\n3. Testing access request serialization:")
    request_dict = access_request.to_dict()
    required_fields = ['requestId', 'userId', 'userRole', 'requestedResource', 'intent', 'duration', 'urgency']
    missing_fields = [field for field in required_fields if field not in request_dict]
    
    if not missing_fields:
        print(f"   ✓ PASS: All required fields present")
    else:
        print(f"   ✗ FAIL: Missing fields: {missing_fields}")
    
    # Test 4: Create from dict
    print("\n4. Testing access request deserialization:")
    access_request2 = AccessRequest.from_dict(request_dict)
    if (access_request2.user_id == access_request.user_id and 
        access_request2.intent == access_request.intent):
        print(f"   ✓ PASS: Access request deserialized correctly")
    else:
        print(f"   ✗ FAIL: Data mismatch")
    
    # Test 5: Invalid intent (too short)
    print("\n5. Testing validation - intent too short:")
    invalid_request = AccessRequest(
        user_id='user123',
        user_role='student',
        requested_resource='library_database',
        intent='short',  # Less than 20 characters
        duration='7 days',
        urgency='medium'
    )
    is_valid, error = invalid_request.validate()
    if not is_valid and 'at least 20 characters' in error:
        print(f"   ✓ PASS: Correctly rejected short intent")
        print(f"   Error message: {error}")
    else:
        print(f"   ✗ FAIL: Should reject short intent")
    
    # Test 6: Invalid intent (too few words)
    print("\n6. Testing validation - intent too few words:")
    invalid_request = AccessRequest(
        user_id='user123',
        user_role='student',
        requested_resource='library_database',
        intent='I need database access urgently',  # Only 5 words but meets char requirement
        duration='7 days',
        urgency='medium'
    )
    # Note: This has 29 chars (>20) but only 5 words, which should pass
    # Let's test with 4 words instead
    invalid_request.intent = 'Need database access urgently'  # 4 words, 29 chars
    is_valid, error = invalid_request.validate()
    if not is_valid and 'at least 5 words' in error:
        print(f"   ✓ PASS: Correctly rejected intent with too few words")
        print(f"   Error message: {error}")
    else:
        print(f"   ✗ FAIL: Should reject intent with too few words")
    
    # Test 7: Invalid urgency
    print("\n7. Testing validation - invalid urgency:")
    invalid_request = AccessRequest(
        user_id='user123',
        user_role='student',
        requested_resource='library_database',
        intent='I need to access the library database for my research project on artificial intelligence',
        duration='7 days',
        urgency='critical'  # Invalid urgency level
    )
    is_valid, error = invalid_request.validate()
    if not is_valid and 'Urgency must be one of' in error:
        print(f"   ✓ PASS: Correctly rejected invalid urgency")
        print(f"   Error message: {error}")
    else:
        print(f"   ✗ FAIL: Should reject invalid urgency")
    
    # Test 8: Set evaluation result
    print("\n8. Testing set evaluation result:")
    evaluation_result = {
        'decision': 'granted',
        'confidenceScore': 85,
        'confidenceBreakdown': {
            'roleMatch': 100,
            'intentClarity': 80,
            'historicalPattern': 75,
            'contextValidity': 90,
            'anomalyScore': 80
        },
        'policiesApplied': ['policy1', 'policy2'],
        'message': 'Access granted based on high confidence score'
    }
    
    access_request.set_evaluation_result(evaluation_result)
    
    if (access_request.decision == 'granted' and 
        access_request.confidence_score == 85 and
        len(access_request.policies_applied) == 2):
        print(f"   ✓ PASS: Evaluation result set correctly")
        print(f"   Decision: {access_request.decision}")
        print(f"   Confidence: {access_request.confidence_score}")
        print(f"   Policies: {access_request.policies_applied}")
    else:
        print(f"   ✗ FAIL: Evaluation result not set correctly")
    
    # Test 9: Metadata fields
    print("\n9. Testing metadata fields:")
    access_request.ip_address = '192.168.1.1'
    access_request.device_info = {
        'userAgent': 'Mozilla/5.0',
        'platform': 'Windows',
        'browser': 'Chrome'
    }
    access_request.session_id = 'session123'
    
    request_dict = access_request.to_dict()
    
    if (request_dict['ipAddress'] == '192.168.1.1' and
        request_dict['deviceInfo']['userAgent'] == 'Mozilla/5.0' and
        request_dict['sessionId'] == 'session123'):
        print(f"   ✓ PASS: Metadata fields stored correctly")
    else:
        print(f"   ✗ FAIL: Metadata fields not stored correctly")
    
    # Test 10: Valid urgency levels
    print("\n10. Testing all valid urgency levels:")
    urgency_levels = ['low', 'medium', 'high']
    all_valid = True
    
    for urgency in urgency_levels:
        test_request = AccessRequest(
            user_id='user123',
            user_role='student',
            requested_resource='library_database',
            intent='I need to access the library database for my research project on artificial intelligence',
            duration='7 days',
            urgency=urgency
        )
        is_valid, error = test_request.validate()
        if not is_valid:
            print(f"   ✗ FAIL: {urgency} should be valid")
            all_valid = False
    
    if all_valid:
        print(f"   ✓ PASS: All urgency levels validated correctly")
    
    print("\n" + "=" * 60)
    print("Access Request Model Tests Completed")
    print("=" * 60)


def test_intent_validation():
    """Test intent validation edge cases"""
    from models.access_request import AccessRequest
    
    print("\n" + "=" * 60)
    print("Testing Intent Validation Edge Cases")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Valid academic intent',
            'intent': 'I need to access the lab server to run machine learning experiments for my thesis research',
            'should_pass': True
        },
        {
            'name': 'Valid work intent',
            'intent': 'I require access to the database to complete the assigned project work for the course',
            'should_pass': True
        },
        {
            'name': 'Exactly 20 characters and 5 words',
            'intent': 'I need access for work',  # 21 chars, 5 words
            'should_pass': True
        },
        {
            'name': 'Exactly 5 words',
            'intent': 'I need database access now',  # Exactly 5 words
            'should_pass': True
        },
        {
            'name': '19 characters (too short)',
            'intent': 'Need access now!!',  # 19 chars
            'should_pass': False
        },
        {
            'name': '4 words (too few)',
            'intent': 'Need database access urgently',  # 4 words but 27 chars
            'should_pass': False
        },
        {
            'name': 'Empty intent',
            'intent': '',
            'should_pass': False
        },
        {
            'name': 'Whitespace only',
            'intent': '     ',
            'should_pass': False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Intent: '{test_case['intent']}'")
        print(f"   Length: {len(test_case['intent'].strip())} chars")
        print(f"   Words: {len(test_case['intent'].strip().split())} words")
        
        request = AccessRequest(
            user_id='user123',
            user_role='student',
            requested_resource='library_database',
            intent=test_case['intent'],
            duration='7 days',
            urgency='medium'
        )
        
        is_valid, error = request.validate()
        
        if test_case['should_pass']:
            if is_valid:
                print(f"   ✓ PASS: Correctly validated")
            else:
                print(f"   ✗ FAIL: Should be valid. Error: {error}")
        else:
            if not is_valid:
                print(f"   ✓ PASS: Correctly rejected. Error: {error}")
            else:
                print(f"   ✗ FAIL: Should be invalid")
    
    print("\n" + "=" * 60)
    print("Intent Validation Tests Completed")
    print("=" * 60)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("ACCESS REQUEST MODEL TEST SUITE")
    print("=" * 60)
    
    try:
        test_access_request_model()
        test_intent_validation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
    
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
