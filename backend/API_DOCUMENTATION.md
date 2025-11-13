# Zero Trust AI Innovations - API Documentation

## Overview

This document provides comprehensive documentation for all API endpoints in the Zero Trust AI Innovations feature set. The system adds 40+ new endpoints for behavioral biometrics, threat prediction, contextual intelligence, collaborative security, adaptive policies, network visualization, session management, security assistant, training simulations, and blockchain audit.

## Base URL

```
Production: https://api.zerotrust.example.com
Development: http://localhost:5000
```

## Authentication

All endpoints require authentication unless otherwise specified. Include the session token in the Authorization header:

```
Authorization: Bearer <session_token>
```

### Authentication Roles

- **User**: Standard authenticated user
- **Admin**: Administrator with elevated privileges
- **Internal**: Service-to-service authentication

## Rate Limiting

Rate limits are applied per user/IP address:

- **Standard endpoints**: 100 requests/minute
- **Behavioral capture**: 120 requests/hour
- **Security reports**: 10 requests/hour
- **Assistant chat**: 60 requests/hour

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699564800
```

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable


### Application Error Codes

```json
{
  "BEHAVIORAL_MODEL_NOT_READY": "User has insufficient baseline data (< 2 weeks)",
  "THREAT_PREDICTION_UNAVAILABLE": "Prediction service temporarily down",
  "CONTEXT_EVALUATION_PARTIAL": "Some context factors unavailable",
  "BLOCKCHAIN_SYNC_DELAYED": "Audit recording delayed but queued",
  "ASSISTANT_OVERLOADED": "Too many concurrent chat requests",
  "INVALID_DEVICE_FINGERPRINT": "Device fingerprint validation failed",
  "CONCURRENT_SESSION_DETECTED": "Multiple active sessions detected",
  "IMPOSSIBLE_TRAVEL_DETECTED": "Location change exceeds physical limits",
  "MODEL_INFERENCE_FAILED": "ML model inference error",
  "EXTERNAL_API_TIMEOUT": "External service timeout"
}
```

## API Endpoints

---

## 1. Behavioral Biometrics Endpoints

### 1.1 Capture Behavioral Data

**Endpoint**: `POST /api/behavioral/capture`

**Description**: Receives and stores behavioral data (keystroke dynamics, mouse movements) from the frontend tracker.

**Authentication**: User role required

**Rate Limit**: 120 requests/hour

**Request Body**:
```json
{
  "userId": "user_12345",
  "keystroke": [
    {
      "key": "a",
      "timestamp": 1699564800123,
      "type": "down"
    },
    {
      "key": "a",
      "timestamp": 1699564800245,
      "type": "up"
    }
  ],
  "mouse": [
    {
      "x": 450,
      "y": 320,
      "timestamp": 1699564800150
    }
  ],
  "timestamp": 1699564800000
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "dataPointsStored": 25,
  "message": "Behavioral data captured successfully"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid data format
- `401 Unauthorized`: Invalid session token
- `429 Too Many Requests`: Rate limit exceeded


### 1.2 Get Risk Score (WebSocket)

**Endpoint**: `GET /api/behavioral/risk-score/:userId`

**Description**: Establishes WebSocket connection for real-time risk score streaming.

**Authentication**: User role required

**WebSocket URL**: `wss://api.zerotrust.example.com/api/behavioral/risk-score/:userId`

**Message Format**:
```json
{
  "userId": "user_12345",
  "riskScore": 45,
  "riskLevel": "medium",
  "timestamp": 1699564800000,
  "factors": {
    "keystrokeAnomaly": 0.35,
    "mouseAnomaly": 0.42,
    "navigationAnomaly": 0.28,
    "timeAnomaly": 0.15
  }
}
```

**Connection Example**:
```javascript
const ws = new WebSocket('wss://api.zerotrust.example.com/api/behavioral/risk-score/user_12345');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Risk Score:', data.riskScore);
};
```

### 1.3 Train Behavioral Model

**Endpoint**: `POST /api/behavioral/train-model`

**Description**: Triggers LSTM model training for a specific user (requires 2 weeks of baseline data).

**Authentication**: Admin role required

**Request Body**:
```json
{
  "userId": "user_12345"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "modelVersion": "v1.2.3",
  "accuracy": 0.96,
  "trainingDataPoints": 15000,
  "message": "Model trained successfully"
}
```

**Error Responses**:
- `400 Bad Request`: Insufficient baseline data
- `403 Forbidden`: Admin role required

---

## 2. Threat Prediction Endpoints

### 2.1 Get Threat Predictions

**Endpoint**: `GET /api/threats/predictions`

**Description**: Retrieves active threat predictions with filtering options.

**Authentication**: Admin role required

**Query Parameters**:
- `timeRange` (optional): `24h`, `48h`, `7d`, `30d` (default: `48h`)
- `confidenceMin` (optional): Minimum confidence level (0-100, default: 70)
- `riskLevel` (optional): `low`, `medium`, `high`, `critical`
- `type` (optional): `brute_force`, `account_takeover`, `privilege_escalation`, `ddos`, `insider_threat`
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Results per page (default: 20, max: 100)

**Request Example**:
```
GET /api/threats/predictions?timeRange=48h&confidenceMin=80&riskLevel=high&page=1&limit=20
```

**Response** (200 OK):
```json
{
  "success": true,
  "predictions": [
    {
      "predictionId": "pred_67890",
      "type": "brute_force",
      "targetUser": "user_12345",
      "targetResource": "admin_panel",
      "confidence": 85,
      "riskLevel": "high",
      "predictedTime": 1699651200000,
      "preventiveMeasures": [
        "Enable additional MFA verification",
        "Temporarily restrict IP range",
        "Monitor login attempts closely"
      ],
      "indicators": [
        {
          "indicator": "failed_attempts_count",
          "value": 8,
          "weight": 0.4
        },
        {
          "indicator": "unusual_time_access",
          "value": true,
          "weight": 0.3
        }
      ],
      "createdAt": 1699564800000
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalResults": 45,
    "limit": 20
  }
}
```


### 2.2 Verify Threat Prediction

**Endpoint**: `POST /api/threats/verify-prediction`

**Description**: Marks a threat prediction outcome as confirmed, false positive, or prevented.

**Authentication**: Admin role required

**Request Body**:
```json
{
  "predictionId": "pred_67890",
  "outcome": "confirmed",
  "notes": "Brute force attack detected and blocked at firewall level"
}
```

**Outcome Values**: `confirmed`, `false_positive`, `prevented`

**Response** (200 OK):
```json
{
  "success": true,
  "accuracyUpdated": 0.82,
  "message": "Prediction outcome recorded"
}
```

### 2.3 Get Threat Indicators

**Endpoint**: `GET /api/threats/indicators/:userId`

**Description**: Retrieves all threat indicators for a specific user.

**Authentication**: Admin role required

**Response** (200 OK):
```json
{
  "success": true,
  "indicators": [
    {
      "indicatorId": "ind_11111",
      "indicatorType": "failed_attempts",
      "severity": "medium",
      "detectedAt": 1699564800000,
      "value": 5,
      "resolved": false,
      "relatedPredictions": ["pred_67890"]
    }
  ]
}
```

---

## 3. Contextual Intelligence Endpoints

### 3.1 Evaluate Context

**Endpoint**: `POST /api/context/evaluate`

**Description**: Evaluates multi-dimensional context for an access request.

**Authentication**: User role required

**Request Body**:
```json
{
  "userId": "user_12345",
  "deviceInfo": {
    "deviceId": "device_abc123",
    "osType": "macOS",
    "osVersion": "14.1",
    "browser": "Chrome",
    "browserVersion": "119.0"
  },
  "networkInfo": {
    "ipAddress": "192.168.1.100",
    "networkType": "campus",
    "vpnActive": true
  },
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "city": "San Francisco",
    "country": "US"
  },
  "timestamp": 1699564800000
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "contextScore": 78,
  "breakdown": {
    "deviceHealth": 85,
    "networkSecurity": 90,
    "timeAppropriateness": 75,
    "locationRisk": 70,
    "historicalTrust": 80
  },
  "recommendation": "approve",
  "requiredVerificationLevel": "none",
  "details": {
    "deviceCompliance": {
      "osUpToDate": true,
      "antivirusActive": true,
      "encryptionEnabled": true,
      "knownDevice": true
    },
    "networkAnalysis": {
      "ipReputation": 95,
      "geoRisk": "low",
      "vpnUsage": true
    },
    "timeAnalysis": {
      "isTypicalTime": true,
      "deviationHours": 0.5
    },
    "locationAnalysis": {
      "impossibleTravel": false,
      "distanceFromLast": 5.2
    }
  }
}
```

**Recommendation Values**: `approve`, `step_up_auth`, `deny`

**Verification Levels**: `none`, `mfa`, `admin_approval`


### 3.2 Get Device Profile

**Endpoint**: `GET /api/context/device-profile/:deviceId`

**Description**: Retrieves device profile and compliance status.

**Authentication**: User role required

**Response** (200 OK):
```json
{
  "success": true,
  "profile": {
    "deviceId": "device_abc123",
    "userId": "user_12345",
    "deviceType": "laptop",
    "osType": "macOS",
    "osVersion": "14.1",
    "browser": "Chrome",
    "browserVersion": "119.0",
    "lastSecurityScan": 1699564800000,
    "complianceStatus": true,
    "complianceChecks": {
      "osUpToDate": true,
      "antivirusInstalled": true,
      "firewallEnabled": true,
      "encryptionEnabled": true
    },
    "registeredDate": 1690000000000,
    "lastUsed": 1699564800000,
    "accessCount": 342
  },
  "trustScore": 85
}
```

---

## 4. Collaborative Security Endpoints

### 4.1 Submit Security Report

**Endpoint**: `POST /api/security/report`

**Description**: Allows users to submit security reports for suspicious activities.

**Authentication**: User role required

**Rate Limit**: 10 requests/hour

**Request Body**:
```json
{
  "reportedBy": "user_12345",
  "reportType": "suspicious_access",
  "targetUserId": "user_67890",
  "targetResource": "sensitive_database",
  "description": "User accessing database at unusual hours with multiple failed queries",
  "severity": "high",
  "evidenceUrls": [
    "https://storage.example.com/screenshots/evidence1.png"
  ]
}
```

**Report Types**: `suspicious_access`, `phishing`, `social_engineering`, `policy_violation`, `other`

**Severity Levels**: `low`, `medium`, `high`, `critical`

**Response** (201 Created):
```json
{
  "success": true,
  "reportId": "report_99999",
  "status": "pending",
  "message": "Security report submitted successfully"
}
```

### 4.2 Get Security Reports

**Endpoint**: `GET /api/security/reports`

**Description**: Retrieves security reports for admin review.

**Authentication**: Admin role required

**Query Parameters**:
- `status` (optional): `pending`, `verified`, `false_positive`, `resolved`
- `severity` (optional): `low`, `medium`, `high`, `critical`
- `reportType` (optional): Report type filter
- `limit` (optional): Results per page (default: 20)
- `page` (optional): Page number (default: 1)

**Response** (200 OK):
```json
{
  "success": true,
  "reports": [
    {
      "reportId": "report_99999",
      "reportedBy": "user_12345",
      "reportType": "suspicious_access",
      "targetUserId": "user_67890",
      "description": "User accessing database at unusual hours...",
      "severity": "high",
      "status": "pending",
      "timestamp": 1699564800000,
      "evidenceUrls": ["https://storage.example.com/screenshots/evidence1.png"]
    }
  ],
  "totalCount": 15,
  "pagination": {
    "currentPage": 1,
    "totalPages": 1,
    "limit": 20
  }
}
```


### 4.3 Verify Security Report

**Endpoint**: `PUT /api/security/report/:reportId/verify`

**Description**: Verifies a security report or marks it as false positive.

**Authentication**: Admin role required

**Request Body**:
```json
{
  "status": "verified",
  "resolution": "Confirmed suspicious access. User account temporarily suspended pending investigation."
}
```

**Status Values**: `verified`, `false_positive`, `resolved`

**Response** (200 OK):
```json
{
  "success": true,
  "reputationUpdated": true,
  "message": "Report verified and reputation updated"
}
```

### 4.4 Get User Reputation

**Endpoint**: `GET /api/security/reputation/:userId`

**Description**: Retrieves user's security reputation score and badges.

**Authentication**: User role required

**Response** (200 OK):
```json
{
  "success": true,
  "reputation": {
    "userId": "user_12345",
    "reportsSubmitted": 15,
    "verifiedReports": 12,
    "falsePositives": 3,
    "reputationScore": 85,
    "badges": [
      {
        "badgeId": "badge_001",
        "name": "Security Sentinel",
        "earnedAt": 1699564800000,
        "icon": "🛡️"
      }
    ],
    "points": 1200,
    "rank": "guardian"
  }
}
```

**Rank Levels**: `novice`, `contributor`, `guardian`, `sentinel`, `champion`

### 4.5 Get Security Leaderboard

**Endpoint**: `GET /api/security/leaderboard`

**Description**: Retrieves security contribution leaderboard.

**Authentication**: User role required

**Query Parameters**:
- `limit` (optional): Number of results (default: 10, max: 100)
- `timeRange` (optional): `week`, `month`, `year`, `all` (default: `month`)

**Response** (200 OK):
```json
{
  "success": true,
  "leaderboard": [
    {
      "userId": "user_12345",
      "username": "john_doe",
      "reputationScore": 95,
      "verifiedReports": 25,
      "rank": "sentinel",
      "badges": 5,
      "position": 1
    }
  ],
  "timeRange": "month"
}
```

---

## 5. Adaptive Policy Endpoints

### 5.1 Get Policy Performance

**Endpoint**: `GET /api/policy/performance`

**Description**: Retrieves policy effectiveness metrics.

**Authentication**: Admin role required

**Query Parameters**:
- `policyId` (optional): Specific policy ID (returns all if omitted)
- `timeRange` (optional): `week`, `month`, `quarter`, `year` (default: `month`)

**Response** (200 OK):
```json
{
  "success": true,
  "performance": [
    {
      "policyId": "policy_001",
      "policyName": "High-Risk Access Control",
      "effectivenessScore": 87,
      "falsePositiveRate": 0.12,
      "falseNegativeRate": 0.05,
      "totalApplications": 1500,
      "truePositives": 120,
      "trueNegatives": 1350,
      "falsePositives": 18,
      "falseNegatives": 12,
      "recommendations": [
        {
          "type": "threshold_adjustment",
          "description": "Increase confidence threshold by 5 points to reduce false positives",
          "expectedImpact": "FPR reduction to 0.08",
          "confidence": 0.85
        }
      ],
      "lastOptimized": 1699564800000
    }
  ]
}
```


### 5.2 Optimize Policy

**Endpoint**: `POST /api/policy/optimize`

**Description**: Triggers policy optimization using ML algorithms.

**Authentication**: Admin role required

**Request Body**:
```json
{
  "policyId": "policy_001",
  "autoApply": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "recommendations": [
    {
      "type": "threshold_adjustment",
      "currentValue": 70,
      "recommendedValue": 75,
      "reason": "High false positive rate detected"
    }
  ],
  "simulatedImpact": {
    "predictedApprovalRateChange": -0.03,
    "predictedFalsePositiveChange": -0.08,
    "predictedEffectivenessChange": 0.05,
    "affectedUsers": 250
  },
  "message": "Optimization recommendations generated"
}
```

### 5.3 Rollback Policy

**Endpoint**: `POST /api/policy/rollback`

**Description**: Reverts policy to a previous version.

**Authentication**: Admin role required

**Request Body**:
```json
{
  "policyId": "policy_001",
  "version": "v1.2.0"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "restoredVersion": "v1.2.0",
  "message": "Policy rolled back successfully"
}
```

### 5.4 Get Policy Evolution

**Endpoint**: `GET /api/policy/evolution/:policyId`

**Description**: Retrieves complete policy change history.

**Authentication**: Admin role required

**Response** (200 OK):
```json
{
  "success": true,
  "evolution": [
    {
      "evolutionId": "evo_001",
      "changeType": "threshold_adjustment",
      "oldValue": 70,
      "newValue": 75,
      "reason": "Automatic optimization - high FPR",
      "triggeredBy": "ml_model",
      "timestamp": 1699564800000,
      "impactMetrics": {
        "approvalRateChange": -0.02,
        "falsePositiveChange": -0.07,
        "effectivenessChange": 0.04
      }
    }
  ]
}
```

---

## 6. Network Visualization Endpoints

### 6.1 Get Network Topology

**Endpoint**: `GET /api/network/topology`

**Description**: Retrieves current network topology data for 3D visualization.

**Authentication**: Admin role required

**Response** (200 OK):
```json
{
  "success": true,
  "resources": [
    {
      "id": "resource_001",
      "name": "Database Server",
      "type": "database",
      "zone": "trusted",
      "x": 10.5,
      "y": 20.3,
      "z": 5.7,
      "activeSessions": 5,
      "securityStatus": "secure"
    }
  ],
  "connections": [
    {
      "from": "user_12345",
      "to": "resource_001",
      "status": "granted",
      "userId": "user_12345",
      "startTime": 1699564800000,
      "riskScore": 25
    }
  ],
  "timestamp": 1699564800000
}
```

**Zone Types**: `trusted`, `monitored`, `threat`

**Connection Status**: `granted`, `denied`, `pending`


### 6.2 Get Network History

**Endpoint**: `GET /api/network/history`

**Description**: Retrieves historical access patterns for playback visualization.

**Authentication**: Admin role required

**Query Parameters**:
- `startTime` (required): Unix timestamp in milliseconds
- `endTime` (required): Unix timestamp in milliseconds
- `userId` (optional): Filter by specific user
- `resourceId` (optional): Filter by specific resource

**Response** (200 OK):
```json
{
  "success": true,
  "timeline": [
    {
      "timestamp": 1699564800000,
      "eventType": "connection_established",
      "userId": "user_12345",
      "resourceId": "resource_001",
      "status": "granted",
      "riskScore": 25
    },
    {
      "timestamp": 1699564860000,
      "eventType": "connection_denied",
      "userId": "user_67890",
      "resourceId": "resource_002",
      "status": "denied",
      "reason": "Insufficient permissions"
    }
  ]
}
```

---

## 7. Session Management Endpoints

### 7.1 Get Active Sessions

**Endpoint**: `GET /api/session/active`

**Description**: Retrieves all active sessions for the authenticated user.

**Authentication**: User role required

**Response** (200 OK):
```json
{
  "success": true,
  "sessions": [
    {
      "sessionId": "session_abc123",
      "deviceId": "device_abc123",
      "startTime": 1699564800000,
      "lastActivity": 1699565000000,
      "currentRiskScore": 35,
      "location": {
        "city": "San Francisco",
        "country": "US"
      },
      "ipAddress": "192.168.1.100",
      "expiresAt": 1699593600000,
      "isCurrent": true
    }
  ]
}
```

### 7.2 Get Session Risk

**Endpoint**: `GET /api/session/risk/:sessionId`

**Description**: Retrieves real-time risk score for a specific session.

**Authentication**: User role required (own sessions) or Admin

**Response** (200 OK):
```json
{
  "success": true,
  "sessionId": "session_abc123",
  "riskScore": 35,
  "riskLevel": "low",
  "factors": {
    "behavioralRisk": 30,
    "contextualRisk": 40,
    "locationRisk": 20,
    "deviceRisk": 25
  },
  "lastUpdated": 1699565000000
}
```

**Risk Levels**: `low` (0-30), `medium` (31-60), `high` (61-80), `critical` (81-100)

### 7.3 Terminate Session

**Endpoint**: `POST /api/session/terminate`

**Description**: Terminates a specific session.

**Authentication**: User role (own sessions) or Admin

**Request Body**:
```json
{
  "sessionId": "session_abc123",
  "reason": "Suspicious activity detected"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "terminated": true,
  "message": "Session terminated successfully"
}
```

### 7.4 Get Session Timeline

**Endpoint**: `GET /api/session/timeline/:sessionId`

**Description**: Retrieves complete activity timeline for a session.

**Authentication**: User role (own sessions) or Admin

**Response** (200 OK):
```json
{
  "success": true,
  "timeline": [
    {
      "timestamp": 1699564800000,
      "action": "session_started",
      "resource": null,
      "riskScoreAtTime": 25
    },
    {
      "timestamp": 1699564850000,
      "action": "resource_accessed",
      "resource": "database_001",
      "riskScoreAtTime": 28
    },
    {
      "timestamp": 1699564900000,
      "action": "behavioral_anomaly_detected",
      "resource": null,
      "riskScoreAtTime": 65
    }
  ]
}
```


---

## 8. Security Assistant Endpoints

### 8.1 Chat with Assistant

**Endpoint**: `POST /api/assistant/chat`

**Description**: Sends a message to the AI security assistant powered by Claude.

**Authentication**: User role required

**Rate Limit**: 60 requests/hour

**Request Body**:
```json
{
  "userId": "user_12345",
  "message": "Why was my access request denied?",
  "conversationHistory": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": 1699564700000
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help you with security today?",
      "timestamp": 1699564705000
    }
  ],
  "context": {
    "requestId": "req_12345"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "response": "Your access request was denied because your current risk score (75) exceeds the threshold for this resource. This was triggered by unusual login time and location change. Would you like me to guide you through additional verification?",
  "confidence": 0.92,
  "conversationId": "conv_abc123",
  "suggestedActions": [
    "Complete MFA verification",
    "Contact administrator"
  ]
}
```

### 8.2 Get Conversation History

**Endpoint**: `GET /api/assistant/conversations/:userId`

**Description**: Retrieves user's conversation history with the assistant.

**Authentication**: User role required

**Query Parameters**:
- `limit` (optional): Number of conversations (default: 10)
- `category` (optional): Filter by category

**Response** (200 OK):
```json
{
  "success": true,
  "conversations": [
    {
      "conversationId": "conv_abc123",
      "startTime": 1699564800000,
      "endTime": 1699565000000,
      "category": "denial_explanation",
      "messageCount": 5,
      "resolved": true,
      "satisfaction": 5
    }
  ]
}
```

**Categories**: `policy_question`, `denial_explanation`, `mfa_help`, `security_report`, `general`

### 8.3 Submit Assistant Feedback

**Endpoint**: `POST /api/assistant/feedback`

**Description**: Submits feedback on assistant response quality.

**Authentication**: User role required

**Request Body**:
```json
{
  "conversationId": "conv_abc123",
  "rating": 5,
  "comment": "Very helpful explanation of the denial reason"
}
```

**Rating**: 1-5 (1 = not helpful, 5 = very helpful)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Feedback submitted successfully"
}
```

---

## 9. Training Simulation Endpoints

### 9.1 Get Available Simulations

**Endpoint**: `GET /api/training/simulations`

**Description**: Retrieves available security training simulations.

**Authentication**: User role required

**Query Parameters**:
- `difficulty` (optional): `beginner`, `intermediate`, `advanced`
- `type` (optional): `phishing`, `social_engineering`, `access_identification`, `password_security`, `breach_response`
- `completed` (optional): `true` to show only completed, `false` for incomplete

**Response** (200 OK):
```json
{
  "success": true,
  "simulations": [
    {
      "simulationId": "sim_001",
      "title": "Phishing Email Detection",
      "type": "phishing",
      "difficulty": "beginner",
      "points": 100,
      "timeLimit": 300,
      "description": "Learn to identify phishing emails",
      "completed": false
    }
  ]
}
```


### 9.2 Get Simulation Details

**Endpoint**: `GET /api/training/simulation/:simulationId`

**Description**: Retrieves detailed information for a specific simulation.

**Authentication**: User role required

**Response** (200 OK):
```json
{
  "success": true,
  "simulation": {
    "simulationId": "sim_001",
    "title": "Phishing Email Detection",
    "type": "phishing",
    "difficulty": "beginner",
    "scenario": "You receive an email claiming to be from IT support...",
    "steps": [
      {
        "stepNumber": 1,
        "description": "Review the email sender address",
        "image": "https://storage.example.com/simulations/phishing1.png",
        "options": [
          {
            "id": "opt_1",
            "text": "The email is legitimate",
            "isCorrect": false
          },
          {
            "id": "opt_2",
            "text": "The email is suspicious - sender domain doesn't match",
            "isCorrect": true
          }
        ]
      }
    ],
    "points": 100,
    "timeLimit": 300
  }
}
```

### 9.3 Complete Simulation

**Endpoint**: `POST /api/training/complete`

**Description**: Submits completed simulation results.

**Authentication**: User role required

**Request Body**:
```json
{
  "simulationId": "sim_001",
  "userId": "user_12345",
  "score": 85,
  "userActions": [
    {
      "step": 1,
      "action": "opt_2",
      "isCorrect": true
    }
  ],
  "completionTime": 245
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "securityAwarenessScore": 78,
  "badgesEarned": [
    {
      "badgeId": "badge_phishing_novice",
      "name": "Phishing Detector",
      "icon": "🎣"
    }
  ],
  "message": "Simulation completed successfully"
}
```

### 9.4 Get Training Progress

**Endpoint**: `GET /api/training/progress/:userId`

**Description**: Retrieves user's training progress and recommendations.

**Authentication**: User role required

**Response** (200 OK):
```json
{
  "success": true,
  "progress": {
    "userId": "user_12345",
    "completedSimulations": 8,
    "securityAwarenessScore": 78,
    "badges": [
      {
        "badgeId": "badge_001",
        "name": "Phishing Detector",
        "earnedAt": 1699564800000
      }
    ],
    "weakAreas": ["password_security"],
    "mandatoryTrainingComplete": false,
    "certificatesEarned": []
  },
  "recommendations": [
    {
      "simulationId": "sim_005",
      "title": "Password Security Best Practices",
      "reason": "Identified weak area"
    }
  ]
}
```

### 9.5 Get Training Leaderboard

**Endpoint**: `GET /api/training/leaderboard`

**Description**: Retrieves training leaderboard rankings.

**Authentication**: User role required

**Query Parameters**:
- `limit` (optional): Number of results (default: 10, max: 100)
- `timeRange` (optional): `week`, `month`, `all` (default: `month`)

**Response** (200 OK):
```json
{
  "success": true,
  "leaderboard": [
    {
      "userId": "user_12345",
      "username": "john_doe",
      "securityAwarenessScore": 95,
      "completedSimulations": 15,
      "badges": 8,
      "rank": "champion",
      "position": 1
    }
  ]
}
```


---

## 10. Blockchain Audit Endpoints

### 10.1 Record Event to Blockchain

**Endpoint**: `POST /api/blockchain/record`

**Description**: Records critical security event to blockchain (internal service use only).

**Authentication**: Internal service authentication

**Request Body**:
```json
{
  "eventType": "access_grant",
  "eventData": {
    "userId": "user_12345",
    "resourceId": "resource_001",
    "timestamp": 1699564800000,
    "approvedBy": "policy_engine"
  }
}
```

**Event Types**: `access_grant`, `access_deny`, `policy_change`, `admin_action`, `mfa_event`

**Response** (200 OK):
```json
{
  "success": true,
  "txHash": "0x1234567890abcdef...",
  "blockNumber": 12345,
  "dataHash": "a1b2c3d4e5f6...",
  "ipfsHash": "QmXyz123...",
  "message": "Event recorded to blockchain"
}
```

### 10.2 Verify Audit Integrity

**Endpoint**: `GET /api/blockchain/verify/:recordId`

**Description**: Verifies audit log integrity against blockchain record.

**Authentication**: Admin role required

**Response** (200 OK):
```json
{
  "success": true,
  "verified": true,
  "recordId": "audit_12345",
  "dataHash": "a1b2c3d4e5f6...",
  "blockchainHash": "a1b2c3d4e5f6...",
  "match": true,
  "txHash": "0x1234567890abcdef...",
  "blockNumber": 12345,
  "timestamp": 1699564800000,
  "message": "Audit log verified successfully"
}
```

**If Tampered**:
```json
{
  "success": true,
  "verified": false,
  "match": false,
  "dataHash": "a1b2c3d4e5f6...",
  "blockchainHash": "x9y8z7w6v5u4...",
  "message": "WARNING: Audit log has been tampered with"
}
```

### 10.3 Browse Blockchain Explorer

**Endpoint**: `GET /api/blockchain/explorer`

**Description**: Browses blockchain audit trail with filtering.

**Authentication**: Admin role required

**Query Parameters**:
- `startBlock` (optional): Starting block number
- `endBlock` (optional): Ending block number
- `eventType` (optional): Filter by event type
- `userId` (optional): Filter by user
- `limit` (optional): Results per page (default: 20)
- `page` (optional): Page number (default: 1)

**Response** (200 OK):
```json
{
  "success": true,
  "events": [
    {
      "recordId": "audit_12345",
      "eventType": "access_grant",
      "txHash": "0x1234567890abcdef...",
      "blockNumber": 12345,
      "timestamp": 1699564800000,
      "dataHash": "a1b2c3d4e5f6...",
      "ipfsHash": "QmXyz123...",
      "verified": true
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalResults": 98
  }
}
```

---

## WebSocket Endpoints

### Real-Time Risk Score Stream

**URL**: `wss://api.zerotrust.example.com/api/behavioral/risk-score/:userId`

**Authentication**: Include token in connection URL or headers

**Message Format**:
```json
{
  "type": "risk_update",
  "userId": "user_12345",
  "riskScore": 45,
  "riskLevel": "medium",
  "timestamp": 1699564800000,
  "factors": {
    "keystrokeAnomaly": 0.35,
    "mouseAnomaly": 0.42,
    "navigationAnomaly": 0.28,
    "timeAnomaly": 0.15
  }
}
```

### Network Topology Updates

**URL**: `wss://api.zerotrust.example.com/api/network/updates`

**Authentication**: Admin role required

**Message Types**:

**Connection Established**:
```json
{
  "type": "connection_established",
  "from": "user_12345",
  "to": "resource_001",
  "timestamp": 1699564800000,
  "riskScore": 25
}
```

**Connection Denied**:
```json
{
  "type": "connection_denied",
  "from": "user_67890",
  "to": "resource_002",
  "timestamp": 1699564800000,
  "reason": "Insufficient permissions"
}
```

**Security Zone Change**:
```json
{
  "type": "zone_change",
  "resourceId": "resource_001",
  "oldZone": "monitored",
  "newZone": "threat",
  "timestamp": 1699564800000
}
```


---

## Code Examples

### JavaScript/Node.js

#### Making Authenticated Requests

```javascript
const axios = require('axios');

const API_BASE_URL = 'https://api.zerotrust.example.com';
const SESSION_TOKEN = 'your_session_token_here';

// Configure axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${SESSION_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Example: Submit security report
async function submitSecurityReport(reportData) {
  try {
    const response = await api.post('/api/security/report', reportData);
    console.log('Report submitted:', response.data);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('Error:', error.response.data);
    }
    throw error;
  }
}

// Example: Get threat predictions
async function getThreatPredictions(filters) {
  try {
    const response = await api.get('/api/threats/predictions', {
      params: filters
    });
    return response.data.predictions;
  } catch (error) {
    console.error('Error fetching predictions:', error);
    throw error;
  }
}
```

#### WebSocket Connection

```javascript
const WebSocket = require('ws');

function connectToRiskScoreStream(userId, token) {
  const ws = new WebSocket(
    `wss://api.zerotrust.example.com/api/behavioral/risk-score/${userId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  ws.on('open', () => {
    console.log('Connected to risk score stream');
  });

  ws.on('message', (data) => {
    const riskData = JSON.parse(data);
    console.log('Risk Score Update:', riskData.riskScore);
    
    if (riskData.riskScore > 80) {
      console.warn('CRITICAL: High risk score detected!');
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });

  ws.on('close', () => {
    console.log('Disconnected from risk score stream');
    // Implement reconnection logic
    setTimeout(() => connectToRiskScoreStream(userId, token), 5000);
  });

  return ws;
}
```

### Python

#### Making Authenticated Requests

```python
import requests
import json

API_BASE_URL = 'https://api.zerotrust.example.com'
SESSION_TOKEN = 'your_session_token_here'

headers = {
    'Authorization': f'Bearer {SESSION_TOKEN}',
    'Content-Type': 'application/json'
}

# Example: Evaluate context
def evaluate_context(context_data):
    response = requests.post(
        f'{API_BASE_URL}/api/context/evaluate',
        headers=headers,
        json=context_data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        print(response.json())
        return None

# Example: Get policy performance
def get_policy_performance(policy_id=None):
    params = {'policyId': policy_id} if policy_id else {}
    response = requests.get(
        f'{API_BASE_URL}/api/policy/performance',
        headers=headers,
        params=params
    )
    
    return response.json()

# Example usage
context = {
    'userId': 'user_12345',
    'deviceInfo': {
        'deviceId': 'device_abc123',
        'osType': 'macOS',
        'osVersion': '14.1'
    },
    'networkInfo': {
        'ipAddress': '192.168.1.100',
        'networkType': 'campus',
        'vpnActive': True
    },
    'location': {
        'latitude': 37.7749,
        'longitude': -122.4194
    },
    'timestamp': 1699564800000
}

result = evaluate_context(context)
print(f"Context Score: {result['contextScore']}")
```

### React/Frontend

#### Behavioral Tracker Integration

```javascript
import { useEffect, useRef } from 'react';
import axios from 'axios';

function useBehavioralTracking(userId) {
  const keystrokeData = useRef([]);
  const mouseData = useRef([]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      keystrokeData.current.push({
        key: e.key,
        timestamp: Date.now(),
        type: 'down'
      });
    };

    const handleKeyUp = (e) => {
      keystrokeData.current.push({
        key: e.key,
        timestamp: Date.now(),
        type: 'up'
      });
    };

    const handleMouseMove = (e) => {
      mouseData.current.push({
        x: e.clientX,
        y: e.clientY,
        timestamp: Date.now()
      });
    };

    // Send data every 30 seconds
    const interval = setInterval(async () => {
      if (keystrokeData.current.length > 0 || mouseData.current.length > 0) {
        try {
          await axios.post('/api/behavioral/capture', {
            userId,
            keystroke: keystrokeData.current,
            mouse: mouseData.current,
            timestamp: Date.now()
          });
          
          keystrokeData.current = [];
          mouseData.current = [];
        } catch (error) {
          console.error('Failed to send behavioral data:', error);
        }
      }
    }, 30000);

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    document.addEventListener('mousemove', handleMouseMove);

    return () => {
      clearInterval(interval);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, [userId]);
}

export default useBehavioralTracking;
```

#### Security Assistant Chat Component

```javascript
import { useState } from 'react';
import axios from 'axios';

function SecurityAssistantChat({ userId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/assistant/chat', {
        userId,
        message: input,
        conversationHistory: messages
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response
      };
      setMessages([...messages, userMessage, assistantMessage]);
    } catch (error) {
      console.error('Assistant error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="security-assistant">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {loading && <div className="loading">Assistant is typing...</div>}
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about security..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default SecurityAssistantChat;
```

---

## Testing with Postman

A Postman collection is available for testing all API endpoints. Import the collection file `Zero_Trust_AI_Innovations.postman_collection.json` into Postman.

### Environment Variables

Set up the following environment variables in Postman:

- `base_url`: API base URL (e.g., `https://api.zerotrust.example.com`)
- `session_token`: Your authentication token
- `user_id`: Test user ID
- `admin_token`: Admin authentication token (for admin endpoints)

### Collection Structure

The Postman collection is organized into folders matching the API endpoint categories:

1. Behavioral Biometrics
2. Threat Prediction
3. Contextual Intelligence
4. Collaborative Security
5. Adaptive Policy
6. Network Visualization
7. Session Management
8. Security Assistant
9. Training Simulations
10. Blockchain Audit

Each folder contains example requests with pre-filled sample data.

---

## Changelog

### Version 1.0.0 (2024-11-13)

- Initial release of Zero Trust AI Innovations API
- 40+ new endpoints across 10 feature categories
- WebSocket support for real-time updates
- Comprehensive authentication and rate limiting
- Full blockchain audit trail integration

---

## Support

For API support, please contact:

- **Technical Support**: support@zerotrust.example.com
- **Documentation Issues**: docs@zerotrust.example.com
- **Security Concerns**: security@zerotrust.example.com

## License

This API documentation is proprietary and confidential. Unauthorized use or distribution is prohibited.
