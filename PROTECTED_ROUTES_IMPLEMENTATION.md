# Protected Routes and Authorization Implementation

## Task 6: Protected Routes and Authorization - COMPLETED ✅

This document summarizes the implementation of protected routes and role-based authorization for the Zero Trust Security Framework.

## Overview

The implementation provides comprehensive route protection on both frontend and backend, ensuring that only authenticated and authorized users can access specific resources based on their roles.

## Frontend Implementation

### 1. ProtectedRoute Component (`frontend/src/components/common/ProtectedRoute.jsx`)

**Purpose:** Wrapper component for protecting routes that require authentication and/or specific roles

#### Features

**Authentication Check:**
- Verifies user is authenticated via AuthContext
- Shows loading spinner while checking auth status
- Redirects to login if not authenticated
- Preserves intended destination in location state

**Role-Based Authorization:**
- Accepts `allowedRoles` prop for role restrictions
- Checks user role against allowed roles
- Redirects to unauthorized page if role doesn't match
- Allows empty array for any authenticated user

**Loading State:**
- Displays centered loading spinner
- Prevents flash of unauthorized content
- User-friendly loading message

#### Props

```javascript
{
  children: ReactNode,        // Protected content
  allowedRoles: string[]      // Array of allowed roles (optional)
}
```

#### Usage Examples

**Any Authenticated User:**
```javascript
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

**Student Only:**
```javascript
<Route
  path="/student/dashboard"
  element={
    <ProtectedRoute allowedRoles={['student']}>
      <StudentDashboard />
    </ProtectedRoute>
  }
/>
```

**Multiple Roles:**
```javascript
<Route
  path="/reports"
  element={
    <ProtectedRoute allowedRoles={['admin', 'faculty']}>
      <Reports />
    </ProtectedRoute>
  }
/>
```

### 2. Unauthorized Component (`frontend/src/components/common/Unauthorized.jsx`)

**Purpose:** Display access denied message when user lacks required permissions

#### Features

**Visual Design:**
- Large lock icon
- Clear "Access Denied" heading
- Explanation of the issue
- Current role display
- Action buttons

**Navigation Options:**
- Go Back button (returns to previous page)
- Go to Dashboard button (role-specific redirect)
- Logout button

**User Information:**
- Shows current user role
- Explains permission requirements
- Suggests contacting administrator

### 3. Dashboard Components

#### StudentDashboard (`frontend/src/components/dashboards/StudentDashboard.jsx`)

**Access:** Students only

**Features:**
- User profile display
- Quick actions (Request Access, View History, Setup MFA)
- Account status (MFA enabled, Active status)
- Logout functionality
- Coming soon notice for full features

#### FacultyDashboard (`frontend/src/components/dashboards/FacultyDashboard.jsx`)

**Access:** Faculty only

**Features:**
- User profile display
- Quick actions (Request Access, View History, View Analytics)
- Account status
- Logout functionality
- Coming soon notice

#### AdminDashboard (`frontend/src/components/dashboards/AdminDashboard.jsx`)

**Access:** Administrators only

**Features:**
- Statistics cards (Total Users, Pending Requests, Active Policies, Security Alerts)
- User profile display
- Admin actions (Manage Users, Manage Policies, View Audit Logs, System Settings)
- Logout functionality
- Coming soon notice

### 4. Route Configuration

**App.js Route Structure:**

```javascript
<Routes>
  {/* Public Routes */}
  <Route path="/login" element={<Login />} />
  <Route path="/signup" element={<Signup />} />
  <Route path="/password-reset" element={<PasswordReset />} />
  <Route path="/unauthorized" element={<Unauthorized />} />
  
  {/* MFA Routes */}
  <Route path="/mfa/setup" element={<MFASetup />} />
  <Route path="/mfa/verify" element={<MFAVerification />} />
  
  {/* Protected Dashboard Routes */}
  <Route
    path="/student/dashboard"
    element={
      <ProtectedRoute allowedRoles={['student']}>
        <StudentDashboard />
      </ProtectedRoute>
    }
  />
  <Route
    path="/faculty/dashboard"
    element={
      <ProtectedRoute allowedRoles={['faculty']}>
        <FacultyDashboard />
      </ProtectedRoute>
    }
  />
  <Route
    path="/admin/dashboard"
    element={
      <ProtectedRoute allowedRoles={['admin']}>
        <AdminDashboard />
      </ProtectedRoute>
    }
  />
  
  {/* Default Routes */}
  <Route path="/" element={<Navigate to="/login" replace />} />
</Routes>
```

## Backend Implementation

### 1. Authorization Middleware (`backend/app/middleware/authorization.py`)

**Purpose:** Provide decorators for protecting API endpoints with authentication and role-based authorization

#### Decorators

**`@require_auth`**
- Verifies JWT session token from cookie
- Extracts user_id, user_role, and user_email
- Adds user information to request object
- Returns 401 if token invalid or missing

**`@require_role(*allowed_roles)`**
- Checks user role against allowed roles
- Must be used after @require_auth
- Returns 403 if role not allowed
- Supports multiple roles

**`@require_admin`**
- Shorthand for @require_role('admin')
- Restricts access to administrators only

**`@require_faculty_or_admin`**
- Shorthand for @require_role('faculty', 'admin')
- Allows faculty and admin access

#### Helper Function

**`get_current_user()`**
- Returns current user information from request
- Must be called within protected route
- Returns dict with user_id, role, email

### 2. User Routes (`backend/app/routes/user_routes.py`)

**Purpose:** API endpoints for user profile and management with role-based access control

#### Endpoints

**GET /api/users/profile**
- Access: Any authenticated user
- Returns: Current user's profile
- Decorator: @require_auth

**PUT /api/users/profile**
- Access: Any authenticated user
- Updates: name, department
- Returns: Updated profile
- Decorator: @require_auth

**GET /api/users/list**
- Access: Admin and Faculty only
- Query params: role (filter), limit (default 50)
- Returns: List of users
- Decorator: @require_auth, @require_role('admin', 'faculty')

**GET /api/users/<user_id>**
- Access: Admin only
- Returns: User data by ID
- Decorator: @require_auth, @require_admin

**POST /api/users/<user_id>/deactivate**
- Access: Admin only
- Action: Deactivates user account
- Prevents: Self-deactivation
- Decorator: @require_auth, @require_admin

**POST /api/users/<user_id>/activate**
- Access: Admin only
- Action: Activates user account
- Decorator: @require_auth, @require_admin

## Security Features

### Frontend Security

**1. Authentication Verification:**
- Checks AuthContext for authenticated status
- Verifies user object exists
- Prevents access to protected routes when not logged in

**2. Role Verification:**
- Compares user role with allowed roles
- Case-sensitive role matching
- Redirects unauthorized users

**3. Loading State Protection:**
- Prevents flash of protected content
- Shows loading indicator during auth check
- Smooth user experience

**4. Location State Preservation:**
- Saves intended destination
- Redirects to original page after login
- Improves user experience

### Backend Security

**1. JWT Token Verification:**
- Validates token signature
- Checks token expiration
- Extracts user claims

**2. Role-Based Access Control:**
- Validates user role on every request
- Prevents privilege escalation
- Granular permission control

**3. Session Management:**
- HttpOnly cookies prevent XSS
- Secure flag requires HTTPS
- SameSite prevents CSRF

**4. Error Handling:**
- Consistent error responses
- Appropriate HTTP status codes
- No sensitive information leakage

## Usage Examples

### Frontend Protected Route

```javascript
// Protect a route for students only
<Route
  path="/student/requests"
  element={
    <ProtectedRoute allowedRoles={['student']}>
      <StudentRequests />
    </ProtectedRoute>
  }
/>

// Protect a route for any authenticated user
<Route
  path="/profile"
  element={
    <ProtectedRoute>
      <UserProfile />
    </ProtectedRoute>
  }
/>
```

### Backend Protected Endpoint

```python
# Require authentication only
@bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    current_user = get_current_user()
    # ... implementation

# Require specific role
@bp.route('/admin/users', methods=['GET'])
@require_auth
@require_role('admin')
def list_all_users():
    # ... implementation

# Require multiple roles
@bp.route('/reports', methods=['GET'])
@require_auth
@require_role('admin', 'faculty')
def get_reports():
    # ... implementation

# Use shorthand decorator
@bp.route('/admin/settings', methods=['PUT'])
@require_auth
@require_admin
def update_settings():
    # ... implementation
```

## Testing

### Manual Testing

**Frontend:**

1. **Unauthenticated Access:**
   ```
   1. Logout or clear cookies
   2. Try to access /student/dashboard
   3. Should redirect to /login
   4. Login state should preserve intended destination
   ```

2. **Wrong Role Access:**
   ```
   1. Login as student
   2. Try to access /admin/dashboard
   3. Should redirect to /unauthorized
   4. Should show current role and error message
   ```

3. **Correct Role Access:**
   ```
   1. Login as student
   2. Access /student/dashboard
   3. Should display dashboard
   4. Should show user information
   ```

**Backend:**

1. **No Token:**
   ```bash
   curl http://localhost:5000/api/users/profile
   # Expected: 401 Unauthorized
   ```

2. **Invalid Token:**
   ```bash
   curl -b "session_token=invalid" http://localhost:5000/api/users/profile
   # Expected: 401 Unauthorized
   ```

3. **Valid Token, Wrong Role:**
   ```bash
   # Login as student, get token
   curl -b "session_token=student_token" http://localhost:5000/api/users/list
   # Expected: 403 Forbidden
   ```

4. **Valid Token, Correct Role:**
   ```bash
   # Login as admin, get token
   curl -b "session_token=admin_token" http://localhost:5000/api/users/list
   # Expected: 200 OK with user list
   ```

### Test Scenarios

**Scenario 1: Student Access**
```
User: student@example.com (role: student)
Can Access:
  - /student/dashboard ✓
  - /profile ✓
  - /mfa/setup ✓

Cannot Access:
  - /faculty/dashboard ✗ (redirects to /unauthorized)
  - /admin/dashboard ✗ (redirects to /unauthorized)
```

**Scenario 2: Faculty Access**
```
User: faculty@example.com (role: faculty)
Can Access:
  - /faculty/dashboard ✓
  - /profile ✓
  - GET /api/users/list ✓

Cannot Access:
  - /student/dashboard ✗
  - /admin/dashboard ✗
  - POST /api/users/<id>/deactivate ✗ (403)
```

**Scenario 3: Admin Access**
```
User: admin@example.com (role: admin)
Can Access:
  - /admin/dashboard ✓
  - All user endpoints ✓
  - All protected routes ✓

Cannot Access:
  - (Admin has full access)
```

## Error Responses

### Frontend

**401 Unauthorized (Not Authenticated):**
- Redirect to: /login
- Preserve: Intended destination in location state

**403 Forbidden (Wrong Role):**
- Redirect to: /unauthorized
- Display: Current role and required permissions

### Backend

**401 Unauthorized:**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authentication required"
  }
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Access denied. Required role: admin"
  }
}
```

## Requirements Satisfied

This implementation satisfies the following requirements:

✅ **Requirement 3.2:** Role-based access control  
✅ **Requirement 3.3:** Route protection based on authentication  
✅ **Requirement 3.4:** Redirect logic for unauthenticated users  
✅ **Requirement 3.5:** Redirect logic for insufficient permissions  
✅ ProtectedRoute component with authentication and role checks  
✅ Role-based route protection (student, faculty, admin)  
✅ Unauthorized page for access denied scenarios  
✅ Backend authorization middleware with JWT validation  
✅ Role-based API endpoint protection  
✅ Dashboard components for each role  

## File Structure

```
frontend/src/
├── components/
│   ├── common/
│   │   ├── ProtectedRoute.jsx      # Route protection wrapper
│   │   └── Unauthorized.jsx        # Access denied page
│   └── dashboards/
│       ├── StudentDashboard.jsx    # Student dashboard
│       ├── FacultyDashboard.jsx    # Faculty dashboard
│       └── AdminDashboard.jsx      # Admin dashboard
└── App.js                          # Updated with protected routes

backend/app/
├── middleware/
│   └── authorization.py            # Auth decorators
├── routes/
│   └── user_routes.py              # Protected user endpoints
└── __init__.py                     # Register user routes
```

## Next Steps

With protected routes implemented, the next tasks will build upon this foundation:

- **Task 7:** Policy Engine Core Logic
- **Task 8:** Intent Analysis Service
- **Task 9:** Access Request Submission (will use protected routes)
- **Task 10:** Access Request History (will use role-based access)

## Future Enhancements

### Planned Improvements

1. **Permission System:**
   - Granular permissions beyond roles
   - Permission groups
   - Dynamic permission assignment

2. **Route Guards:**
   - Time-based access restrictions
   - IP-based restrictions
   - Device-based restrictions

3. **Audit Logging:**
   - Log all authorization failures
   - Track access patterns
   - Alert on suspicious activity

4. **Session Management:**
   - Multiple active sessions
   - Session revocation
   - Device management

5. **Advanced Authorization:**
   - Resource-level permissions
   - Attribute-based access control (ABAC)
   - Policy-based authorization

## Troubleshooting

### Frontend Issues

**Issue:** Infinite redirect loop
**Solution:**
- Check that login page is not protected
- Verify AuthContext is properly initialized
- Check for circular redirects

**Issue:** Protected route shows briefly before redirect
**Solution:**
- Ensure loading state is checked first
- Add loading spinner
- Use Navigate component for redirects

**Issue:** User role not recognized
**Solution:**
- Verify user object has role property
- Check role string matches exactly (case-sensitive)
- Ensure AuthContext is providing user data

### Backend Issues

**Issue:** 401 on valid requests
**Solution:**
- Check cookie is being sent (withCredentials: true)
- Verify JWT secret matches
- Check token hasn't expired

**Issue:** 403 on authorized requests
**Solution:**
- Verify user role in JWT payload
- Check decorator order (@require_auth before @require_role)
- Ensure role string matches exactly

**Issue:** Decorator not working
**Solution:**
- Check decorator order (auth before role)
- Verify @wraps(f) is used
- Check function signature

## Additional Resources

- [React Router Protected Routes](https://reactrouter.com/en/main/start/tutorial#protected-routes)
- [Flask Decorators](https://flask.palletsprojects.com/en/2.3.x/patterns/viewdecorators/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
