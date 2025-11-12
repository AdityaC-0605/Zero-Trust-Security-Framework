# Task 18: Session Management - Implementation Complete

## Overview
Implemented comprehensive session management with JWT tokens, refresh token rotation, CSRF protection, inactivity timeout, and automatic session expiration.

## Backend Implementation

### 1. Enhanced Authentication Service (`backend/app/services/auth_service.py`)

#### New Features:
- **Refresh Token Generation**: 7-day expiration with unique token IDs
- **CSRF Token Generation**: Secure random tokens for state-changing operations
- **Token Rotation**: Refresh tokens are rotated on each use to prevent replay attacks
- **Inactivity Tracking**: Last activity timestamp stored in JWT and Firestore
- **Session Invalidation**: Methods to invalidate single or all user sessions

#### Key Methods Added:
- `create_session()`: Returns access token, refresh token, and CSRF token
- `refresh_session_with_token()`: Validates and rotates refresh tokens
- `verify_session_token()`: Checks token validity and inactivity timeout
- `verify_csrf_token()`: Validates CSRF tokens for state-changing operations
- `update_last_activity()`: Updates activity timestamp in Firestore
- `invalidate_session()`: Removes session from database
- `invalidate_all_sessions()`: Security measure for compromised accounts
- `create_access_token_with_activity()`: Creates new token with updated activity

#### Configuration Variables:
- `JWT_EXPIRATION_MINUTES`: 60 (access token lifetime)
- `REFRESH_TOKEN_EXPIRATION_DAYS`: 7 (refresh token lifetime)
- `SESSION_INACTIVITY_MINUTES`: 30 (inactivity timeout)

### 2. Updated Authentication Routes (`backend/app/routes/auth_routes.py`)

#### Enhanced Endpoints:

**POST /api/auth/verify**
- Sets three cookies: `session_token`, `refresh_token`, `csrf_token`
- All cookies use HttpOnly, Secure, SameSite=Strict (except CSRF which needs JS access)

**POST /api/auth/refresh**
- Uses refresh token from cookie (not request body)
- Implements token rotation - issues new refresh token
- Detects and prevents replay attacks
- Clears all cookies on failure

**POST /api/auth/logout**
- Invalidates session in database
- Clears all three cookies

**POST /api/auth/activity** (NEW)
- Updates last activity timestamp
- Prevents inactivity timeout

**GET /api/auth/session/status** (NEW)
- Returns session information
- Shows remaining time before expiration
- Shows remaining time before inactivity timeout

### 3. Enhanced Authorization Middleware (`backend/app/middleware/authorization.py`)

#### Updates:
- Checks inactivity timeout on every request
- Updates activity timestamp for non-GET requests
- Clears cookies automatically on session expiration
- Returns appropriate error codes for different failure scenarios

### 4. CSRF Protection Middleware (`backend/app/middleware/csrf_protection.py`)

#### Features:
- Decorator `@require_csrf` for state-changing endpoints
- Validates CSRF token from `X-CSRF-Token` header
- Skips validation for GET, HEAD, OPTIONS requests
- Returns 403 Forbidden on validation failure

### 5. Cookie Configuration

All cookies use secure settings:
```python
httponly=True      # Prevents JavaScript access (except CSRF token)
secure=True        # Requires HTTPS
samesite='Strict'  # Prevents CSRF attacks
```

**Cookie Lifetimes:**
- `session_token`: 60 minutes
- `refresh_token`: 7 days
- `csrf_token`: 7 days

## Frontend Implementation

### 1. Enhanced Auth Service (`frontend/src/services/authService.js`)

#### New Methods:
- `refreshSession()`: Uses refresh token from cookie
- `updateActivity()`: Pings server to update activity
- `getSessionStatus()`: Retrieves session information
- `getCsrfToken()`: Extracts CSRF token from cookie

#### Axios Interceptor:
- Automatically adds CSRF token to state-changing requests
- Reads token from cookie and adds to `X-CSRF-Token` header

### 2. Session Manager Hook (`frontend/src/hooks/useSessionManager.js`)

#### Features:
- **Activity Tracking**: Monitors user interactions (mouse, keyboard, scroll, touch)
- **Inactivity Timeout**: 30-minute timeout with automatic logout
- **Automatic Token Refresh**: Refreshes token every 50 minutes (before 60-minute expiration)
- **Activity Updates**: Sends activity ping every 5 minutes
- **Session Status Check**: Warns if session is about to expire

#### Configuration:
```javascript
INACTIVITY_TIMEOUT: 30 minutes
TOKEN_REFRESH_INTERVAL: 50 minutes
ACTIVITY_UPDATE_INTERVAL: 5 minutes
```

### 3. Axios Interceptors (`frontend/src/utils/axiosInterceptors.js`)

#### Error Handling:
- **401 Errors**: Attempts automatic token refresh
- **Token Expiration**: Refreshes token and retries request
- **CSRF Errors**: Refreshes session to get new CSRF token
- **Request Queuing**: Queues requests during token refresh
- **Automatic Redirect**: Redirects to login on refresh failure

### 4. Session Manager Component (`frontend/src/components/common/SessionManager.jsx`)

- Invisible component that manages session in background
- Integrated into App.js at root level
- Uses useSessionManager hook

### 5. Updated Auth Context (`frontend/src/contexts/AuthContext.jsx`)

#### Changes:
- Stores CSRF token in localStorage
- Clears CSRF token on logout
- Handles CSRF token in login and refresh flows

### 6. App Integration (`frontend/src/App.js`)

#### Updates:
- Imports and includes `<SessionManager />`
- Calls `setupAxiosInterceptors()` on mount
- Ensures session management is active throughout app

## Security Features Implemented

### 1. JWT Token Storage
✅ HttpOnly cookies prevent XSS attacks
✅ Secure flag requires HTTPS
✅ SameSite=Strict prevents CSRF attacks

### 2. Token Expiration
✅ Access tokens expire after 60 minutes
✅ Automatic expiration check on every request
✅ User prompted to re-authenticate on expiration

### 3. Session Timeout
✅ 30-minute inactivity timeout
✅ Activity tracked on user interactions
✅ Automatic logout on timeout

### 4. Token Refresh
✅ Refresh token rotation prevents replay attacks
✅ Automatic refresh before expiration
✅ Failed refresh invalidates all sessions

### 5. CSRF Protection
✅ CSRF tokens required for state-changing operations
✅ Tokens validated on server side
✅ Tokens rotated with refresh tokens

### 6. Session Invalidation
✅ Logout clears all cookies
✅ Database session removed on logout
✅ All sessions can be invalidated for security

## Testing

Created `backend/test_session_management.py` with tests for:
- Session creation with all tokens
- Token verification
- Refresh token rotation
- CSRF token validation
- Session invalidation
- Activity tracking
- Token expiration handling

Note: Tests require Firebase configuration to run fully.

## Environment Variables

Added to `.env.example`:
```bash
REFRESH_TOKEN_EXPIRATION_DAYS=7
SESSION_INACTIVITY_MINUTES=30
```

## Requirements Satisfied

✅ **10.1**: JWT tokens stored in HttpOnly, Secure, SameSite=Strict cookies
✅ **10.2**: Automatic session expiration after 60 minutes of token age
✅ **10.3**: Session timeout after 30 minutes of inactivity
✅ **10.4**: Token refresh mechanism with refresh token rotation
✅ **10.5**: CSRF protection on all state-changing endpoints
✅ Clear all cookies and invalidate session on logout
✅ Prompt user to re-authenticate when token expires

## Usage Examples

### Backend - Protecting Routes with CSRF

```python
from app.middleware.csrf_protection import require_csrf
from app.middleware.authorization import require_auth

@bp.route('/api/resource', methods=['POST'])
@require_auth
@require_csrf
def create_resource():
    # This endpoint is protected by both auth and CSRF
    pass
```

### Frontend - Automatic CSRF Handling

```javascript
// CSRF token is automatically added to all POST/PUT/DELETE requests
await axios.post('/api/resource', data, { withCredentials: true });
```

### Frontend - Using Session Manager

```javascript
// In App.js - already integrated
import SessionManager from './components/common/SessionManager';

function App() {
  return (
    <AuthProvider>
      <SessionManager />
      {/* rest of app */}
    </AuthProvider>
  );
}
```

## Files Modified

### Backend:
- `backend/app/services/auth_service.py` - Enhanced with refresh tokens and CSRF
- `backend/app/routes/auth_routes.py` - Updated endpoints for new session flow
- `backend/app/middleware/authorization.py` - Added inactivity checking
- `backend/app/middleware/csrf_protection.py` - NEW: CSRF protection decorator
- `backend/.env.example` - Added new configuration variables

### Frontend:
- `frontend/src/services/authService.js` - Added session management methods
- `frontend/src/contexts/AuthContext.jsx` - Updated for CSRF token handling
- `frontend/src/hooks/useSessionManager.js` - NEW: Session management hook
- `frontend/src/components/common/SessionManager.jsx` - NEW: Session manager component
- `frontend/src/components/common/index.js` - Export SessionManager
- `frontend/src/utils/axiosInterceptors.js` - NEW: Request/response interceptors
- `frontend/src/App.js` - Integrated session manager

### Testing:
- `backend/test_session_management.py` - NEW: Session management tests

## Next Steps

1. **Deploy with HTTPS**: Secure cookies require HTTPS in production
2. **Configure Firebase**: Set up Firebase credentials for full functionality
3. **Monitor Sessions**: Add logging for session-related events
4. **Rate Limiting**: Apply rate limits to refresh endpoint
5. **Session Analytics**: Track session duration and timeout patterns

## Notes

- All session data is stored in Firestore `sessions` collection
- Refresh tokens are single-use (rotated on each refresh)
- CSRF tokens are accessible to JavaScript (needed for headers)
- Activity tracking is passive and doesn't block user interactions
- Token refresh happens automatically in the background
- Failed refresh attempts redirect user to login page
