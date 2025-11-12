# Policy Engine Implementation

## Overview
Successfully implemented the Policy Engine Core Logic for the Zero Trust Security Framework. The policy engine evaluates access requests against defined policies and calculates confidence scores using weighted factors.

## Files Created

### 1. `backend/app/services/policy_engine.py`
Main policy engine service with the following methods:

- **`evaluate_request(request_data)`**: Main orchestrator that evaluates access requests
- **`match_policies(resource_type, user_role)`**: Finds applicable policies based on resource type and role
- **`calculate_confidence_score(request_data, user_history)`**: Calculates weighted confidence score (0-100)
- **`check_role_match(user_role, resource_type)`**: Validates user role against allowed roles (30% weight)
- **`validate_context(request_data)`**: Checks time restrictions and device info (15% weight)
- **`make_decision(confidence_score, policy, breakdown)`**: Makes access decision based on thresholds

#### Confidence Score Weights:
- Role Match: 30%
- Intent Clarity: 25%
- Historical Pattern: 20%
- Context Validity: 15%
- Anomaly Detection: 10%

#### Decision Thresholds:
- ≥90: Auto-approve (granted)
- 50-89: Require MFA (granted_with_mfa)
- <50: Deny (denied)

### 2. `backend/app/models/policy.py`
Policy model with Firestore integration:

- **Policy class**: Data model with validation
- **`create_policy()`**: Create new policy in Firestore
- **`get_policy_by_id()`**: Retrieve policy by ID
- **`get_all_policies()`**: Get all policies (with active filter)
- **`update_policy()`**: Update existing policy
- **`delete_policy()`**: Soft delete (deactivate) policy
- **`create_default_policies()`**: Create default policies for common resources

#### Default Policies Created:
1. **Lab Server Access**: Faculty/Admin only, 70% min confidence, MFA required, time-restricted (6 AM - 10 PM)
2. **Library Database Access**: All roles, 60% min confidence, no MFA required
3. **Admin Panel Access**: Admin only, 90% min confidence, MFA required

### 3. Updated Files
- `backend/app/models/__init__.py`: Exported Policy model and functions
- `backend/app/services/__init__.py`: Exported policy_engine singleton

### 4. `backend/test_policy_engine.py`
Comprehensive test suite covering:
- Policy matching by resource and role
- Role match validation
- Intent analysis
- Context validation
- Confidence score calculation
- Decision making logic
- Full request evaluation
- Policy model validation

## Test Results
All tests passed successfully:
- ✓ Policy model creation and validation
- ✓ Policy matching for different roles and resources
- ✓ Role match scoring (100 for exact match)
- ✓ Intent analysis (good intent: 75, bad intent: 10)
- ✓ Context validation (100 for valid context)
- ✓ Confidence score calculation (80.5 for test request)
- ✓ Decision thresholds (auto-approve, MFA, deny)
- ✓ Full request evaluation

## Key Features Implemented

### 1. Policy Matching
- Matches policies based on resource type and user role
- Supports wildcard matching
- Sorts by priority (highest first)

### 2. Confidence Scoring
- Multi-factor weighted scoring system
- Role match validation
- Intent clarity analysis with keyword detection
- Historical pattern evaluation
- Context validation (time, device, IP)
- Anomaly detection

### 3. Intent Analysis
- Academic keyword detection (+20 points)
- Legitimate keyword detection (+15 points)
- Suspicious keyword detection (-30 points)
- Minimum length and word count validation
- Text coherence bonus

### 4. Context Validation
- Time restriction enforcement (hour and day)
- Device information validation
- IP address tracking
- Policy-specific restrictions

### 5. Decision Making
- Three-tier decision system (grant, MFA, deny)
- Policy minimum confidence enforcement
- Detailed denial reasons
- MFA requirement logic

## Requirements Satisfied
- ✓ 5.1: Policy-based evaluation with applicable policy matching
- ✓ 5.2: Confidence score calculation with weighted factors
- ✓ 5.3: Auto-approve at ≥90, MFA at 50-89, deny at <50
- ✓ 5.4: Role match validation
- ✓ 5.5: Context validation with time restrictions
- ✓ 11.2: Policy configuration with rules and priority
- ✓ 11.3: Active status management

## Usage Example

```python
from app.services import policy_engine

# Evaluate an access request
request_data = {
    'userId': 'user123',
    'userRole': 'faculty',
    'requestedResource': 'lab_server',
    'intent': 'Need to run ML experiments for research',
    'duration': '7 days',
    'urgency': 'medium',
    'timestamp': datetime.utcnow(),
    'ipAddress': '192.168.1.1',
    'deviceInfo': {'userAgent': 'Mozilla/5.0'}
}

result = policy_engine.evaluate_request(request_data)

# Result contains:
# - decision: 'granted', 'granted_with_mfa', or 'denied'
# - confidenceScore: 0-100
# - message: Human-readable message
# - policiesApplied: List of policy IDs
# - confidenceBreakdown: Individual component scores
# - mfaRequired: Boolean
```

## Next Steps
The policy engine is ready for integration with:
- Task 8: Intent Analysis Service (can be enhanced)
- Task 9: Access Request Submission (will use evaluate_request)
- Task 11: Audit Logging System (should log all evaluations)
- Task 16: Policy Configuration (admin interface for policies)

## Notes
- Policy engine uses singleton pattern for easy access
- All methods include error handling and logging
- Firestore integration ready (requires credentials)
- Extensible design for future enhancements
