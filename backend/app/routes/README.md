# Authentication Routes

This module contains the authentication API endpoints for the Zero Trust Security Framework.

## Endpoints

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "idToken": "firebase_id_token",
  "name": "User Name",
  "role": "student|faculty|admin",
  "department": "Computer Science",
  "studentId": "12345" // Required for students
}
```

**Response:**
```json
{
  "success": true,
  "user": { /* user data */ },
  "message": "Registration successful"
}
```

### POST /api/auth/verify
Verify Firebase ID token and create session.

**Request Body:**
```json
{
  "idToken": "firebase_id_token"
}
```

**Response:**
- Sets HttpOnly session cookie
- Returns user data and session token

### POST /api/auth/refresh
Refresh session token.

**Request Body:**
```json
{
  "idToken": "firebase_id_token"
}
```

### POST /api/auth/logout
Logout user and clear session.

**Requires:** Authentication

### POST /api/auth/mfa/setup
Setup MFA for user account.

**Requires:** Authentication

**Response:**
```json
{
  "success": true,
  "secret": "base32_secret",
  "qrCodeUri": "otpauth://..."
}
```

### POST /api/auth/mfa/verify
Verify MFA code.

**Requires:** Authentication

**Request Body:**
```json
{
  "code": "123456"
}
```

## Security Features

- JWT tokens with 60-minute expiration
- HttpOnly, Secure, SameSite cookies
- Failed login attempt tracking (5 attempts max)
- Account lockout after max attempts (30 minutes)
- MFA lockout after 3 failed attempts
- IP address and device tracking
