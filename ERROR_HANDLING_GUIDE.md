# Error Handling and Validation Guide

## Overview

This document describes the comprehensive error handling and validation system implemented in the Zero Trust Security Framework. The system provides consistent error responses, automatic retry logic, field-level validation, and comprehensive error logging.

## Architecture

### Frontend Error Handling

#### 1. Axios Interceptors (`frontend/src/utils/axiosInterceptors.js`)

The Axios interceptor provides global error handling for all HTTP requests:

**Features:**
- Automatic retry logic for network errors and 500+ server errors (1 retry after 2 seconds)
- Automatic token refresh on 401 errors
- CSRF token refresh on 403 errors
- User-friendly error notifications
- Request queuing during token refresh

**Error Types Handled:**
- Network errors (no response)
- 401 Unauthorized (session expired)
- 403 Forbidden (permission denied, CSRF errors)
- 404 Not Found
- 429 Rate Limit Exceeded
- 500+ Server Errors

**Usage:**
```javascript
import { setupAxiosInterceptors, setNotificationContext } from './utils/axiosInterceptors';

// In App.js
useEffect(() => {
  setupAxiosInterceptors();
  setNotificationContext(notificationContext);
}, [notificationContext]);
```

#### 2. Form Validation (`frontend/src/utils/formValidation.js`)

Provides validation functions for form fields with user-friendly error messages:

**Available Validators:**
- `validateEmail(email)` - Email format validation
- `validatePassword(password, options)` - Password strength validation
- `validatePasswordConfirmation(password, confirmPassword)` - Password matching
- `validateRequired(value, fieldName)` - Required field validation
- `validateLength(text, options)` - Text length validation
- `validateWordCount(text, options)` - Word count validation
- `validateIntent(intent)` - Intent description validation (20+ chars, 5+ words)
- `validateMFACode(code)` - 6-digit MFA code validation
- `validateEnum(value, allowedValues, fieldName)` - Enum validation
- `validateForm(formData, validationRules)` - Multi-field form validation

**Usage Example:**
```javascript
import { validateEmail, validatePassword, validateForm } from './utils/formValidation';

// Single field validation
const emailResult = validateEmail(email);
if (!emailResult.isValid) {
  setErrors({ ...errors, email: emailResult.error });
}

// Multi-field form validation
const validationRules = {
  email: [validateEmail],
  password: [validatePassword]
};

const { isValid, errors } = validateForm(formData, validationRules);
if (!isValid) {
  setErrors(errors);
}
```

**Extracting API Errors:**
```javascript
import { extractFieldErrors, getErrorMessage } from './utils/formValidation';

try {
  await axios.post('/api/endpoint', data);
} catch (error) {
  // Extract field-level errors
  const fieldErrors = extractFieldErrors(error);
  setErrors(fieldErrors);
  
  // Get general error message
  const message = getErrorMessage(error);
  showNotification(message);
}
```

### Backend Error Handling

#### 1. Error Handler Utility (`backend/app/utils/error_handler.py`)

Provides custom exception classes and error handling utilities:

**Custom Exception Classes:**
- `AppError` - Base application error
- `ValidationError` - Validation errors (400)
- `AuthenticationError` - Authentication errors (401)
- `AuthorizationError` - Authorization errors (403)
- `NotFoundError` - Resource not found (404)
- `RateLimitError` - Rate limit exceeded (429)

**Usage in Routes:**
```python
from app.utils.error_handler import (
    ValidationError,
    AuthenticationError,
    NotFoundError,
    handle_errors,
    validate_required_fields,
    validate_field_length,
    validate_enum
)

@bp.route('/endpoint', methods=['POST'])
@handle_errors  # Decorator for automatic error handling
def my_endpoint():
    data = request.get_json()
    
    # Validate required fields
    validate_required_fields(data, ['email', 'password'])
    
    # Validate field length
    validate_field_length(data['password'], 'password', min_length=8)
    
    # Validate enum
    validate_enum(data['role'], 'role', ['student', 'faculty', 'admin'])
    
    # Raise custom errors
    if not user_exists:
        raise NotFoundError('User not found', resource_type='user')
    
    return jsonify({'success': True, 'data': result})
```

**Validation Functions:**
- `validate_required_fields(data, required_fields)` - Check required fields
- `validate_field_length(value, field_name, min_length, max_length)` - Length validation
- `validate_enum(value, field_name, allowed_values)` - Enum validation
- `validate_email(email)` - Email format validation
- `validate_word_count(text, field_name, min_words)` - Word count validation

#### 2. Global Error Handlers (`backend/app/__init__.py`)

Flask error handlers for HTTP status codes:

**Handled Status Codes:**
- 400 Bad Request - Validation errors
- 401 Unauthorized - Authentication required
- 403 Forbidden - Permission denied
- 404 Not Found - Resource not found
- 405 Method Not Allowed
- 413 Payload Too Large
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error
- All unhandled exceptions

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "fieldName",
      "additionalInfo": "value"
    }
  }
}
```

## Error Codes

### Authentication Errors (401)
- `AUTH_REQUIRED` - Authentication required
- `AUTH_INVALID_TOKEN` - Invalid or expired token
- `AUTH_FAILED` - Authentication failed
- `AUTH_ACCOUNT_LOCKED` - Account locked due to failed attempts

### Authorization Errors (403)
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `CSRF_TOKEN_MISSING` - CSRF token not provided
- `CSRF_TOKEN_INVALID` - CSRF token validation failed
- `USER_DISABLED` - User account is disabled

### Validation Errors (400)
- `VALIDATION_ERROR` - Input validation failed
- `MISSING_REQUIRED_FIELD` - Required field not provided

### Resource Errors (404)
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `USER_NOT_FOUND` - User not found
- `ENDPOINT_NOT_FOUND` - API endpoint not found

### Rate Limit Errors (429)
- `RATE_LIMIT_EXCEEDED` - Too many requests

### Server Errors (500)
- `INTERNAL_ERROR` - Unexpected server error
- `SYSTEM_ERROR` - System-level error

## Audit Logging

All errors are automatically logged to the audit system with:
- Event type (application_error, system_error, validation_error)
- User ID (if authenticated)
- Action and resource
- Error details and stack traces
- Severity level (low, medium, high, critical)

**Severity Levels:**
- `low` - Validation errors, user input errors
- `medium` - Rate limit exceeded, authorization failures
- `high` - Application errors, authentication failures
- `critical` - System errors, unhandled exceptions

## Retry Logic

### Frontend Retry
- Network errors: 1 retry after 2 seconds
- 500+ server errors: 1 retry after 2 seconds
- Token refresh: Automatic with request queuing

### Backend Retry
Not implemented at the backend level. Clients should implement retry logic.

## Best Practices

### Frontend

1. **Always validate forms before submission:**
```javascript
const { isValid, errors } = validateForm(formData, validationRules);
if (!isValid) {
  setErrors(errors);
  return;
}
```

2. **Handle API errors gracefully:**
```javascript
try {
  const response = await axios.post('/api/endpoint', data);
  // Handle success
} catch (error) {
  const fieldErrors = extractFieldErrors(error);
  setErrors(fieldErrors);
  
  const message = getErrorMessage(error);
  showNotification({ type: 'error', message });
}
```

3. **Display field-level errors:**
```jsx
<input
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  className={errors.email ? 'error' : ''}
/>
{errors.email && <span className="error-message">{errors.email}</span>}
```

### Backend

1. **Use custom exceptions for known errors:**
```python
if not user:
    raise NotFoundError('User not found', resource_type='user')

if user.role not in allowed_roles:
    raise AuthorizationError('Insufficient permissions')
```

2. **Validate input early:**
```python
validate_required_fields(data, ['email', 'password', 'name'])
validate_email(data['email'])
validate_field_length(data['password'], 'password', min_length=8)
```

3. **Use the @handle_errors decorator:**
```python
@bp.route('/endpoint', methods=['POST'])
@handle_errors
def my_endpoint():
    # Your code here
    # Exceptions are automatically caught and logged
```

4. **Provide detailed error messages:**
```python
raise ValidationError(
    message='Password must contain at least one uppercase letter',
    field='password',
    details={'requirement': 'uppercase'}
)
```

## Testing

### Frontend Tests
Run form validation tests:
```bash
cd frontend
npm test -- formValidation.test.js
```

### Backend Tests
Run error handling tests:
```bash
cd backend
python -m pytest test_error_handling.py -v
```

## Monitoring

All errors are logged to:
1. **Audit Logs** - Firestore `auditLogs` collection
2. **Console** - stderr for debugging
3. **Notifications** - Real-time alerts for high-severity events

Query audit logs for errors:
```javascript
// Get all errors in the last 24 hours
const logs = await db.collection('auditLogs')
  .where('eventType', 'in', ['application_error', 'system_error'])
  .where('timestamp', '>', yesterday)
  .orderBy('timestamp', 'desc')
  .get();
```

## Troubleshooting

### Issue: Errors not showing in UI
**Solution:** Ensure notification context is set in axios interceptors:
```javascript
setNotificationContext(notificationContext);
```

### Issue: Validation errors not displayed
**Solution:** Check that field names in validation rules match form field names.

### Issue: Retry logic not working
**Solution:** Verify that `_retryCount` is not already set on the request config.

### Issue: CSRF token errors
**Solution:** Ensure CSRF token is included in cookies and sent with state-changing requests.

## Future Enhancements

1. **Structured logging** - Integrate with external logging service (e.g., Sentry)
2. **Error analytics** - Track error rates and patterns
3. **Custom error pages** - User-friendly error pages for different error types
4. **Internationalization** - Multi-language error messages
5. **Error recovery suggestions** - Provide actionable suggestions for common errors
