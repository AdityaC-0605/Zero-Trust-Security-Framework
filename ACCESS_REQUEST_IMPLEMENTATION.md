# Access Request Submission Implementation

This document describes the implementation of the Access Request Submission feature (Task 9) for the Zero Trust Security Framework.

## Overview

The Access Request Submission feature allows users to submit requests for accessing protected resources. The system evaluates each request using the policy engine and returns a decision with a confidence score.

## Components Implemented

### Backend Components

#### 1. AccessRequest Model (`backend/app/models/access_request.py`)

The AccessRequest model defines the data structure for access requests stored in Firestore.

**Key Features:**
- Validates intent description (minimum 20 characters, 5 words)
- Supports multiple urgency levels (low, medium, high)
- Captures metadata (IP address, device info, timestamp)
- Stores evaluation results (decision, confidence score, breakdown)

**Validation Rules:**
- Intent must be at least 20 characters
- Intent must contain at least 5 words
- Urgency must be one of: low, medium, high
- All required fields must be present

#### 2. Access Routes (`backend/app/routes/access_routes.py`)

API endpoints for access request management.

**Endpoints:**

- **POST /api/access/request** - Submit new access request
  - Validates request data
  - Captures client IP and device information
  - Evaluates request using policy engine
  - Creates notification for user
  - Returns decision with confidence score

- **GET /api/access/history** - Get user's access request history
  - Supports filtering by status
  - Supports pagination (limit, offset)
  - Returns list of user's requests

- **GET /api/access/:id** - Get detailed request information
  - Returns full request details
  - Includes confidence score breakdown
  - Enforces authorization (users can only view their own requests)

### Frontend Components

#### 1. RequestForm Component (`frontend/src/components/access/RequestForm.jsx`)

React component for submitting access requests.

**Features:**
- Resource dropdown selection (lab_server, library_database, etc.)
- Intent textarea with character and word count validation
- Duration selection (1 hour to 3 months)
- Urgency level radio buttons (low, medium, high)
- Real-time form validation
- Loading states during submission
- Success/error notifications
- Displays decision result with confidence score

**Validation:**
- Resource selection required
- Intent minimum 20 characters and 5 words
- Duration selection required
- Urgency level required

#### 2. StudentDashboard Integration

The RequestForm component has been integrated into the StudentDashboard:
- Toggle button to show/hide request form
- Success callback for handling submitted requests
- Seamless integration with existing dashboard layout

## API Request/Response Examples

### Submit Access Request

**Request:**
```http
POST /api/access/request
Content-Type: application/json
Cookie: session_token=<token>

{
  "resource": "lab_server",
  "intent": "I need to access the lab server to run machine learning experiments for my thesis research on neural networks",
  "duration": "7 days",
  "urgency": "medium"
}
```

**Response (Success):**
```json
{
  "success": true,
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "decision": "granted_with_mfa",
  "confidenceScore": 75,
  "message": "Access granted with MFA verification required",
  "mfaRequired": true,
  "confidenceBreakdown": {
    "roleMatch": 100,
    "intentClarity": 80,
    "historicalPattern": 50,
    "contextValidity": 90,
    "anomalyScore": 85
  },
  "policiesApplied": ["policy1"]
}
```

**Response (Validation Error):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Intent must be at least 20 characters"
  }
}
```

### Get Access History

**Request:**
```http
GET /api/access/history?status=granted&limit=10&offset=0
Cookie: session_token=<token>
```

**Response:**
```json
{
  "success": true,
  "requests": [
    {
      "requestId": "550e8400-e29b-41d4-a716-446655440000",
      "userId": "user123",
      "userRole": "student",
      "requestedResource": "lab_server",
      "intent": "I need to access...",
      "duration": "7 days",
      "urgency": "medium",
      "decision": "granted",
      "confidenceScore": 85,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "totalCount": 25,
  "limit": 10,
  "offset": 0
}
```

## Integration with Policy Engine

The access request submission integrates with the existing policy engine:

1. **Request Evaluation**: Each submitted request is evaluated by the policy engine
2. **Confidence Scoring**: The engine calculates a weighted confidence score based on:
   - Role match (30%)
   - Intent clarity (25%)
   - Historical pattern (20%)
   - Context validity (15%)
   - Anomaly detection (10%)
3. **Decision Making**: Based on the confidence score:
   - ≥90: Auto-approve
   - 50-89: Approve with MFA required
   - <50: Deny

## Notification System

When an access request is submitted, a notification is automatically created:
- Stored in Firestore `notifications` collection
- Contains decision result and message
- Links to the access request for details
- Expires after 30 days

## Security Features

1. **Authentication Required**: All endpoints require valid session token
2. **Authorization**: Users can only view their own requests (admins can view all)
3. **Input Validation**: Strict validation on all input fields
4. **Metadata Capture**: IP address and device info captured for audit trail
5. **Rate Limiting**: Prevents abuse (10 requests per hour per user)

## Testing

Comprehensive tests have been implemented in `backend/test_access_request.py`:
- Model validation tests
- Intent validation edge cases
- Serialization/deserialization tests
- Metadata handling tests

All tests pass successfully.

## Requirements Satisfied

This implementation satisfies the following requirements from the design document:

- **Requirement 4.1**: Access request submission with required fields
- **Requirement 4.2**: Intent validation (minimum 20 characters, 5 words)
- **Requirement 4.3**: Metadata capture (IP address, device info, timestamp)
- **Requirement 4.4**: Unique request ID assignment
- **Requirement 4.5**: Confirmation notification to user
- **Requirement 5.1**: Policy engine evaluation integration

## Future Enhancements

Potential improvements for future iterations:
1. Real-time request status updates via WebSocket
2. Request history filtering by date range
3. Request resubmission for denied requests
4. Bulk request submission
5. Request templates for common access patterns
