# Context Providers and State Management Implementation

## Task 5: Context Providers and State Management - COMPLETED ✅

This document summarizes the implementation of global state management using React Context API for the Zero Trust Security Framework.

## Overview

The application uses React Context API to manage global state for authentication and notifications. This provides a centralized way to access and update user authentication status and display notifications throughout the application.

## Context Providers Implemented

### 1. AuthContext (`frontend/src/contexts/AuthContext.jsx`)

**Purpose:** Global authentication state management

#### State Variables

```javascript
{
  user: {
    userId: string,
    email: string,
    role: string,
    name: string,
    department: string,
    mfaEnabled: boolean,
    // ... other user fields
  } | null,
  loading: boolean,
  authenticated: boolean
}
```

#### Methods

**`login(email, password)`**
- Authenticates user with email and password
- Updates user state and authenticated status
- Persists user data to localStorage
- Returns: Promise<result>

**`logout()`**
- Clears user session
- Removes user data from localStorage
- Resets authentication state
- Returns: Promise<void>

**`refreshAuth()`**
- Refreshes authentication state from backend
- Updates user data if session is valid
- Clears state if session expired
- Returns: Promise<result>

**`updateUser(userData)`**
- Updates user profile data
- Merges new data with existing user object
- Persists changes to localStorage
- Parameters: userData (object)

#### Features

**Persistence:**
- User data stored in localStorage
- Automatic restoration on page refresh
- Cleared on logout

**Firebase Integration:**
- Listens to Firebase auth state changes
- Auto-refreshes session when Firebase user changes
- Syncs with backend session management

**Error Handling:**
- Graceful handling of network errors
- Automatic state cleanup on errors
- Console logging for debugging

#### Usage Example

```javascript
import { useAuth } from './contexts/AuthContext';

function MyComponent() {
  const { user, authenticated, loading, login, logout } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome, {user.name}!</h1>
      <p>Role: {user.role}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### 2. NotificationContext (`frontend/src/contexts/NotificationContext.jsx`)

**Purpose:** Real-time notification management

#### State Variables

```javascript
{
  notifications: [
    {
      id: number,
      type: 'success' | 'error' | 'warning' | 'info',
      title: string,
      message: string,
      timestamp: string,
      read: boolean
    }
  ],
  unreadCount: number
}
```

#### Methods

**`addNotification(notification)`**
- Adds new notification to the list
- Generates unique ID and timestamp
- Increments unread count
- Auto-dismisses success/info after 5 seconds
- Parameters: { type, title, message }
- Returns: notificationId

**`removeNotification(notificationId)`**
- Removes notification from list
- Updates unread count if notification was unread
- Parameters: notificationId (number)

**`markAsRead(notificationId)`**
- Marks specific notification as read
- Decrements unread count
- Parameters: notificationId (number)

**`markAllAsRead()`**
- Marks all notifications as read
- Resets unread count to 0

**`clearAll()`**
- Removes all notifications
- Resets unread count to 0

**`getUnreadNotifications()`**
- Returns array of unread notifications
- Returns: Array<notification>

#### Features

**Auto-Dismiss:**
- Success notifications: 5 seconds
- Info notifications: 5 seconds
- Error notifications: 7 seconds
- Warning notifications: 7 seconds

**Notification Types:**
- `success` - Green, checkmark icon
- `error` - Red, X icon
- `warning` - Yellow, exclamation icon
- `info` - Blue, info icon

**Unread Tracking:**
- Automatic count management
- Badge display support
- Mark as read functionality

#### Usage Example

```javascript
import { useNotifications } from './contexts/NotificationContext';

function MyComponent() {
  const { notifications, unreadCount, addNotification, markAsRead } = useNotifications();

  const handleAction = async () => {
    try {
      // Perform action
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Action completed successfully'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.message
      });
    }
  };

  return (
    <div>
      <button onClick={handleAction}>Perform Action</button>
      <div>Unread: {unreadCount}</div>
    </div>
  );
}
```

## Toast Notification Component

### ToastContainer (`frontend/src/components/common/Toast.jsx`)

**Purpose:** Display toast notifications in the UI

#### Features

**Visual Design:**
- Fixed position (top-right corner)
- Stacked notifications (max 5 visible)
- Color-coded by type
- Icons for each type
- Close button on each toast

**Animations:**
- Smooth entry/exit
- Auto-dismiss with timer
- Manual dismiss on click

**Accessibility:**
- Screen reader friendly
- Keyboard accessible close button
- ARIA labels

#### Notification Styling

**Success (Green):**
- Background: green-50
- Text: green-800
- Icon: Checkmark

**Error (Red):**
- Background: red-50
- Text: red-800
- Icon: X mark

**Warning (Yellow):**
- Background: yellow-50
- Text: yellow-800
- Icon: Exclamation

**Info (Blue):**
- Background: blue-50
- Text: blue-800
- Icon: Info circle

## Application Integration

### App.js Structure

```javascript
<AuthProvider>
  <NotificationProvider>
    <Router>
      <ToastContainer />
      <Routes>
        {/* Routes */}
      </Routes>
    </Router>
  </NotificationProvider>
</AuthProvider>
```

**Provider Order:**
1. AuthProvider (outermost)
2. NotificationProvider
3. Router
4. ToastContainer (inside Router)

**Why This Order:**
- AuthProvider first so all components can access auth state
- NotificationProvider second for notification access
- Router inside providers for route-based logic
- ToastContainer inside Router for consistent display

## Integration with Components

### Login Component Integration

**Before:**
```javascript
const result = await authService.login(email, password);
```

**After:**
```javascript
const { login } = useAuth();
const { addNotification } = useNotifications();

const result = await login(email, password);
addNotification({
  type: 'success',
  title: 'Login Successful',
  message: `Welcome back, ${result.user.name}!`
});
```

### Benefits of Integration

1. **Centralized State:**
   - Single source of truth for user data
   - Consistent state across components
   - No prop drilling

2. **Automatic Persistence:**
   - User data saved to localStorage
   - Survives page refreshes
   - Automatic cleanup on logout

3. **Real-time Updates:**
   - Firebase auth state listener
   - Automatic session refresh
   - Instant UI updates

4. **User Feedback:**
   - Toast notifications for all actions
   - Success/error messages
   - Auto-dismiss for better UX

## LocalStorage Schema

### User Data

**Key:** `user`

**Value:**
```json
{
  "userId": "firebase_uid",
  "email": "user@example.com",
  "role": "student",
  "name": "John Doe",
  "department": "Computer Science",
  "studentId": "12345678",
  "mfaEnabled": false,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "lastLogin": "2024-01-15T10:30:00.000Z",
  "isActive": true
}
```

**Lifecycle:**
- Set: On successful login
- Updated: On user profile changes
- Cleared: On logout or session expiration

## Error Handling

### AuthContext Error Handling

**Network Errors:**
```javascript
try {
  await login(email, password);
} catch (error) {
  // State automatically cleared
  // Error logged to console
  // User notified via UI
}
```

**Session Expiration:**
```javascript
// Automatic detection via Firebase listener
// State cleared automatically
// User redirected to login
```

**Invalid Credentials:**
```javascript
// Error message displayed
// State remains unauthenticated
// User can retry
```

### NotificationContext Error Handling

**Duplicate Notifications:**
- Each notification gets unique ID
- No duplicate prevention (by design)
- User can dismiss individually

**Memory Management:**
- Auto-dismiss prevents accumulation
- Manual clear all option
- Max 5 visible at once

## Performance Considerations

### AuthContext Optimization

**Memoization:**
- Context value object stable reference
- Prevents unnecessary re-renders
- useCallback for methods

**Lazy Loading:**
- User data loaded on demand
- Firebase listener only when needed
- Cleanup on unmount

### NotificationContext Optimization

**useCallback:**
- All methods wrapped in useCallback
- Stable function references
- Prevents child re-renders

**Notification Limit:**
- Only 5 notifications displayed
- Older notifications hidden
- Prevents DOM bloat

## Testing

### Manual Testing

**AuthContext:**
```bash
# Test login
1. Login with valid credentials
2. Check user state in React DevTools
3. Refresh page - user should persist
4. Logout - state should clear

# Test session refresh
1. Login
2. Wait for token to expire
3. Perform action requiring auth
4. Session should auto-refresh

# Test error handling
1. Login with invalid credentials
2. Check error state
3. Verify state remains unauthenticated
```

**NotificationContext:**
```bash
# Test notifications
1. Trigger success notification
2. Should auto-dismiss after 5 seconds
3. Trigger error notification
4. Should stay until dismissed
5. Add multiple notifications
6. Only 5 should be visible

# Test unread count
1. Add notification
2. Unread count should increment
3. Mark as read
4. Unread count should decrement
```

### Test Scenarios

**Login Flow:**
```javascript
// 1. Initial state
authenticated: false
user: null
loading: true

// 2. After login
authenticated: true
user: { ...userData }
loading: false

// 3. After logout
authenticated: false
user: null
loading: false
```

**Notification Flow:**
```javascript
// 1. Add notification
notifications: [{ id: 1, type: 'success', ... }]
unreadCount: 1

// 2. Mark as read
notifications: [{ id: 1, type: 'success', read: true, ... }]
unreadCount: 0

// 3. Auto-dismiss
notifications: []
unreadCount: 0
```

## Requirements Satisfied

This implementation satisfies the following requirements:

✅ **Requirement 9.5:** Real-time notification system  
✅ **Requirement 15.1:** User state management  
✅ **Requirement 15.2:** Session persistence  
✅ AuthContext with user state, loading, and authenticated status  
✅ NotificationContext with notifications array and unread count  
✅ login, logout, refreshAuth, and updateUser methods  
✅ addNotification, markAsRead, and clearAll methods  
✅ App.jsx wrapped with both context providers  
✅ Authentication state persisted to localStorage  
✅ Toast notification component for user feedback  

## File Structure

```
frontend/src/
├── contexts/
│   ├── AuthContext.jsx          # Authentication state management
│   ├── NotificationContext.jsx  # Notification state management
│   └── index.js                 # Export all contexts
├── components/
│   ├── common/
│   │   └── Toast.jsx            # Toast notification component
│   └── auth/
│       └── Login.jsx            # Updated with context integration
└── App.js                       # Wrapped with providers
```

## Next Steps

With context providers implemented, the next tasks will leverage this infrastructure:

- **Task 6:** Protected Routes (use AuthContext for route protection)
- **Task 7:** Policy Engine (notifications for access decisions)
- **Task 9:** Access Requests (notifications for request status)
- **Task 11:** Audit Logging (notifications for security events)

## Future Enhancements

### Planned Improvements

1. **Persistent Notifications:**
   - Store in localStorage
   - Survive page refreshes
   - Sync across tabs

2. **Notification Center:**
   - Dropdown with all notifications
   - Mark all as read
   - Filter by type
   - Search functionality

3. **Real-time Updates:**
   - WebSocket integration
   - Server-sent events
   - Push notifications

4. **Advanced Auth Features:**
   - Remember me functionality
   - Multiple sessions
   - Device management
   - Session timeout warnings

5. **Performance:**
   - Virtual scrolling for notifications
   - Lazy loading user data
   - Optimistic updates
   - Request deduplication

## Troubleshooting

### User State Not Persisting

**Issue:** User logged out on page refresh
**Solution:**
- Check localStorage in browser DevTools
- Verify JSON.parse doesn't throw error
- Check Firebase auth state listener

### Notifications Not Displaying

**Issue:** Toast notifications don't appear
**Solution:**
- Check ToastContainer is rendered
- Verify z-index (should be 50)
- Check notification type is valid
- Verify NotificationProvider wraps component

### Context Not Available

**Issue:** "useAuth must be used within AuthProvider"
**Solution:**
- Verify AuthProvider wraps App
- Check import path is correct
- Ensure component is inside provider tree

### Memory Leaks

**Issue:** Notifications accumulate
**Solution:**
- Check auto-dismiss timers
- Verify cleanup in useEffect
- Limit visible notifications to 5

## Additional Resources

- [React Context API Documentation](https://react.dev/reference/react/useContext)
- [React Hooks Documentation](https://react.dev/reference/react)
- [localStorage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [Firebase Auth State Listener](https://firebase.google.com/docs/auth/web/manage-users)
