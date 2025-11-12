# Authentication Setup Guide

This guide explains the Firebase Integration and Authentication Service implementation for the Zero Trust Security Framework.

## Overview

Task 2 has been completed with the following components:

### Frontend Components
1. **firebaseConfig.js** - Firebase SDK configuration
2. **authService.js** - Authentication service with login, signup, logout, and password reset methods

### Backend Components
1. **firebase_config.py** - Firebase Admin SDK configuration (already existed, enhanced)
2. **auth_service.py** - Authentication service with token verification, session management, and MFA
3. **user.py** - User model with Firestore schema validation
4. **auth_routes.py** - API endpoints for authentication operations

## Features Implemented

### ✅ Firebase SDK Configuration
- Frontend: Firebase Authentication SDK configured with environment variables
- Backend: Firebase Admin SDK configured with service account credentials

### ✅ Authentication Service (Frontend)
- `login(email, password)` - User login with Firebase Authentication
- `signup(userData)` - User registration with email verification
- `logout()` - User logout and session cleanup
- `resetPassword(email)` - Password reset email
- `refreshSession()` - Session token refresh
- `getCurrentUser()` - Get current authenticated user
- `getIdToken()` - Get Firebase ID token

### ✅ Authentication Service (Backend)
- `verify_firebase_token(id_token)` - Verify Firebase ID tokens
- `create_session(user_id, user_data)` - Create JWT session tokens
- `verify_session_token(token)` - Verify JWT tokens
- `refresh_session(id_token)` - Refresh session tokens
- `check_login_attempts(user_id, ip_address)` - Track failed login attempts
- `record_failed_login(user_id, ip_address)` - Record failed attempts
- `record_successful_login(user_id, ip_address, device_info)` - Record successful logins
- `setup_mfa(user_id)` - Generate MFA secret and QR code
- `verify_mfa_code(user_id, code)` - Verify TOTP codes

### ✅ User Model
- Complete Firestore schema with validation
- Fields: userId, email, role, name, department, studentId, mfaEnabled, mfaSecret, etc.
- Helper functions: create_user_document, get_user_by_id, get_user_by_email, update_user
- Email and role validation
- Public data filtering (excludes sensitive fields)

### ✅ API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/verify` - Token verification and session creation
- `POST /api/auth/refresh` - Session refresh
- `POST /api/auth/logout` - User logout
- `POST /api/auth/mfa/setup` - MFA setup
- `POST /api/auth/mfa/verify` - MFA verification

### ✅ Security Features
- JWT tokens with 60-minute expiration
- HttpOnly, Secure, SameSite=Strict cookies
- Failed login tracking (max 5 attempts)
- Account lockout after max attempts (30 minutes)
- MFA secret encryption with AES-256
- MFA lockout after 3 failed attempts
- IP address and device tracking
- Email verification requirement

## Setup Instructions

### 1. Firebase Project Setup

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firebase Authentication with Email/Password provider
3. Enable Firestore Database
4. Download service account credentials:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save as `backend/firebase-credentials.json`

### 2. Frontend Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp frontend/.env.example frontend/.env
   ```

2. Update `frontend/.env` with your Firebase config:
   ```
   REACT_APP_FIREBASE_API_KEY=your_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=your_project_id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   REACT_APP_FIREBASE_APP_ID=your_app_id
   REACT_APP_API_URL=http://localhost:5000/api
   ```

### 3. Backend Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Update `backend/.env`:
   ```
   SECRET_KEY=your_secret_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   ENCRYPTION_KEY=your_encryption_key_here
   ```

3. Generate encryption key (Python):
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

### 4. Install Dependencies

Frontend:
```bash
cd frontend
npm install
```

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run the Application

Backend:
```bash
cd backend
source venv/bin/activate
python run.py
```

Frontend:
```bash
cd frontend
npm start
```

## Testing the Implementation

### 1. Test User Registration

```javascript
import authService from './services/authService';

const userData = {
  email: 'test@example.com',
  password: 'SecurePass123!',
  name: 'Test User',
  role: 'student',
  department: 'Computer Science',
  studentId: '12345'
};

authService.signup(userData)
  .then(result => console.log('Signup successful:', result))
  .catch(error => console.error('Signup failed:', error));
```

### 2. Test User Login

```javascript
authService.login('test@example.com', 'SecurePass123!')
  .then(result => console.log('Login successful:', result))
  .catch(error => console.error('Login failed:', error));
```

### 3. Test MFA Setup

```javascript
// After login
authService.getIdToken()
  .then(token => {
    return axios.post('http://localhost:5000/api/auth/mfa/setup', {}, {
      withCredentials: true
    });
  })
  .then(response => console.log('MFA setup:', response.data))
  .catch(error => console.error('MFA setup failed:', error));
```

## API Usage Examples

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "idToken": "firebase_id_token",
    "name": "John Doe",
    "role": "student",
    "department": "Computer Science",
    "studentId": "12345"
  }'
```

### Verify Token and Create Session
```bash
curl -X POST http://localhost:5000/api/auth/verify \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "idToken": "firebase_id_token"
  }'
```

### Setup MFA
```bash
curl -X POST http://localhost:5000/api/auth/mfa/setup \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

### Verify MFA Code
```bash
curl -X POST http://localhost:5000/api/auth/mfa/verify \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "code": "123456"
  }'
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files or Firebase credentials to version control
2. **HTTPS**: In production, ensure all communication uses HTTPS
3. **Encryption Key**: Use a secure, persistent encryption key in production
4. **Cookie Settings**: Secure cookies require HTTPS in production
5. **Rate Limiting**: Consider adding rate limiting middleware for production
6. **Email Verification**: Users must verify email before logging in

## Firestore Collections

### users
```javascript
{
  userId: string,
  email: string,
  role: "student" | "faculty" | "admin",
  name: string,
  department: string,
  studentId: string,
  mfaEnabled: boolean,
  mfaSecret: string (encrypted),
  createdAt: timestamp,
  lastLogin: timestamp,
  isActive: boolean,
  failedLoginAttempts: number,
  lockoutUntil: timestamp,
  mfaFailedAttempts: number,
  metadata: {
    lastIpAddress: string,
    lastDeviceInfo: object
  }
}
```

## Requirements Satisfied

This implementation satisfies the following requirements from the design document:

- **Requirement 1.1**: User authentication with email and password
- **Requirement 1.2**: JWT token creation with 60-minute expiration
- **Requirement 1.3**: Account lockout after 5 failed attempts
- **Requirement 1.4**: Email verification for new users
- **Requirement 1.5**: Password reset functionality
- **Requirement 2.1-2.5**: Multi-factor authentication with TOTP
- **Requirement 10.1**: HttpOnly, Secure, SameSite cookies
- **Requirement 10.2**: Session expiration after 60 minutes
- **Requirement 10.3**: Session invalidation on logout

## Next Steps

The authentication foundation is now complete. The next tasks will build upon this:

- Task 3: Authentication UI Components (Login, Signup, MFA, Password Reset)
- Task 4: Multi-Factor Authentication UI
- Task 5: Context Providers and State Management
- Task 6: Protected Routes and Authorization

## Troubleshooting

### Firebase Credentials Not Found
- Ensure `firebase-credentials.json` is in the `backend` directory
- Check `FIREBASE_CREDENTIALS_PATH` in `.env`

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate`

### CORS Errors
- Check `CORS_ORIGINS` in backend `.env`
- Ensure frontend URL matches CORS configuration

### Cookie Not Set
- Check browser console for cookie errors
- Ensure `withCredentials: true` in axios requests
- In development, you may need to adjust cookie security settings
