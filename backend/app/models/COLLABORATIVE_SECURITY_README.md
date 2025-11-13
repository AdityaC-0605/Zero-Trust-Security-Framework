# Collaborative Security Scoring System

## Overview

The Collaborative Security Scoring system enables users to actively participate in campus security by reporting suspicious activities, earning reputation points, and contributing to a safer environment through gamification.

## Features

### 1. Security Reporting System

Users can submit security reports for various types of concerns:
- Suspicious access attempts
- Phishing attempts
- Social engineering
- Policy violations
- Data breaches
- Unauthorized access
- Other security concerns

**Rate Limiting**: 10 reports per hour per user

### 2. Reputation Scoring System

Users earn reputation through security contributions:

**Points System**:
- Report submitted: +5 points
- Report verified as accurate: +10 points
- Report marked as false positive: -5 points

**Reputation Score Calculation**:
```python
accuracy = (verified_reports / total_reports) * 100
penalty = (false_positives / total_reports) * 50
reputation_score = max(0, min(100, accuracy - penalty))
```

**Rank System**:
- Novice: 0-49 points
- Contributor: 50-99 points
- Guardian: 100-199 points
- Sentinel: 200-499 points
- Champion: 500+ points

**Badges**:
- Security Novice: 10 verified reports
- Security Contributor: 25 verified reports
- Security Guardian: 50 verified reports

### 3. Gamification Features

**Leaderboard**:
- Ranks users by total points
- Displays verified reports and reputation scores
- Shows earned badges
- Highlights top 3 contributors with medals

**Priority System**:
- Reports from users with reputation score > 80 are prioritized
- High-reputation users' reports appear at the top of admin queue

**Resource Sensitivity Voting**:
- Community-driven sensitivity ratings for resources
- Consensus-based classification (Public, Internal, Confidential, Restricted, Critical)
- Vote distribution visualization

## API Endpoints

### POST /api/security/report
Submit a security report

**Request Body**:
```json
{
  "reportedBy": "user_id",
  "reportType": "suspicious_access",
  "targetUserId": "optional_user_id",
  "targetResource": "optional_resource",
  "description": "Detailed description",
  "severity": "medium",
  "evidenceUrls": []
}
```

**Response**:
```json
{
  "success": true,
  "reportId": "report_id",
  "status": "pending"
}
```

### GET /api/security/reports
Get security reports (admin only)

**Query Parameters**:
- `status`: Filter by status (pending, verified, false_positive, resolved)
- `severity`: Filter by severity (low, medium, high, critical)
- `limit`: Maximum number of reports (default: 100)

### PUT /api/security/report/:reportId/verify
Verify or mark report as false positive (admin only)

**Request Body**:
```json
{
  "status": "verified",
  "resolution": "Resolution notes"
}
```

### GET /api/security/reputation/:userId
Get user's security reputation

**Response**:
```json
{
  "success": true,
  "reputation": {
    "userId": "user_id",
    "reportsSubmitted": 15,
    "verifiedReports": 12,
    "falsePositives": 2,
    "reputationScore": 75,
    "badges": [],
    "points": 125,
    "rank": "guardian",
    "contributionHistory": []
  },
  "rank": "guardian"
}
```

### GET /api/security/leaderboard
Get security contribution leaderboard

**Query Parameters**:
- `limit`: Maximum number of entries (default: 100)

## Frontend Components

### SecurityReportForm
Modal form for submitting security reports with validation

**Props**:
- `isOpen`: Boolean to control modal visibility
- `onClose`: Function to close modal
- `onSubmit`: Function to handle form submission

### SecurityReportQueue
Admin interface for reviewing and verifying reports

**Features**:
- Filter by status (pending, verified, false_positive, resolved)
- Priority highlighting for high-reputation reporters
- Inline verification with resolution notes

### ReputationProfile
Detailed view of user's security reputation

**Displays**:
- Current rank and reputation score
- Total points and progress to next rank
- Statistics (reports submitted, verified, false positives, accuracy)
- Earned badges
- Recent contribution history

### SecurityLeaderboard
Community leaderboard showing top contributors

**Features**:
- Medal display for top 3 positions
- User stats (points, verified reports, reputation score)
- Badge display
- Current user highlighting
- Rank legend

### ReputationBadge
Compact badge component showing user rank and score

### ResourceSensitivityVoting
Community voting interface for resource sensitivity levels

**Features**:
- 5-level sensitivity scale (Public to Critical)
- Consensus calculation
- Vote distribution visualization
- Thank you confirmation after voting

### SecurityDashboard
Comprehensive dashboard combining all security features

**Tabs**:
- Leaderboard view
- Personal reputation profile

## Data Models

### SecurityReport
```python
{
  "reportId": "string",
  "reportedBy": "string",
  "reportType": "string",
  "targetUserId": "string",
  "targetResource": "string",
  "description": "string",
  "severity": "string",
  "status": "string",
  "verifiedBy": "string",
  "timestamp": "datetime",
  "resolution": "string",
  "evidenceUrls": ["array"],
  "relatedIncidents": ["array"]
}
```

### UserSecurityReputation
```python
{
  "userId": "string",
  "reportsSubmitted": "number",
  "verifiedReports": "number",
  "falsePositives": "number",
  "reputationScore": "number",
  "badges": ["array"],
  "points": "number",
  "rank": "string",
  "contributionHistory": ["array"]
}
```

## Usage Examples

### Submitting a Report (Frontend)
```javascript
import { SecurityReportForm } from './components/security';

const handleSubmit = async (reportData) => {
  const response = await axios.post('/api/security/report', {
    reportedBy: userId,
    ...reportData
  });
  return response.data;
};

<SecurityReportForm
  isOpen={showForm}
  onClose={() => setShowForm(false)}
  onSubmit={handleSubmit}
/>
```

### Displaying Leaderboard
```javascript
import { SecurityLeaderboard } from './components/security';

<SecurityLeaderboard limit={50} />
```

### Admin Review Queue
```javascript
import { SecurityReportQueue } from './components/security';

<SecurityReportQueue />
```

## Security Considerations

1. **Rate Limiting**: Prevents spam by limiting reports to 10 per hour
2. **Authentication**: All endpoints require valid user authentication
3. **Authorization**: Admin-only endpoints verify admin role
4. **Validation**: All inputs are validated before processing
5. **Audit Logging**: All security reports and verifications are logged

## Future Enhancements

1. Real-time notifications for report status updates
2. Advanced analytics dashboard for security trends
3. Integration with threat prediction system
4. Automated report verification using ML
5. Team-based competitions and challenges
6. Monthly/yearly security champion awards
7. Integration with blockchain for immutable report records
