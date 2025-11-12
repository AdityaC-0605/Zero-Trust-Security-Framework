# Environment Setup Guide

This guide provides detailed instructions for setting up environment variables for both development and production environments.

## Table of Contents

1. [Frontend Environment Variables](#frontend-environment-variables)
2. [Backend Environment Variables](#backend-environment-variables)
3. [Generating Secure Secrets](#generating-secure-secrets)
4. [Firebase Configuration](#firebase-configuration)
5. [Email Configuration](#email-configuration)
6. [Monitoring Configuration](#monitoring-configuration)
7. [Platform-Specific Setup](#platform-specific-setup)

---

## Frontend Environment Variables

### Development (.env)

Create `frontend/.env` for local development:

```env
# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id

# Backend API URL
REACT_APP_API_URL=http://localhost:5000/api

# Optional: Sentry for error tracking
REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx

# Optional: Application version
REACT_APP_VERSION=1.0.0
```

### Production (.env.production)

Create `frontend/.env.production` for production:

```env
# Firebase Configuration (Production)
REACT_APP_FIREBASE_API_KEY=${REACT_APP_FIREBASE_API_KEY}
REACT_APP_FIREBASE_AUTH_DOMAIN=${REACT_APP_FIREBASE_AUTH_DOMAIN}
REACT_APP_FIREBASE_PROJECT_ID=${REACT_APP_FIREBASE_PROJECT_ID}
REACT_APP_FIREBASE_STORAGE_BUCKET=${REACT_APP_FIREBASE_STORAGE_BUCKET}
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=${REACT_APP_FIREBASE_MESSAGING_SENDER_ID}
REACT_APP_FIREBASE_APP_ID=${REACT_APP_FIREBASE_APP_ID}

# Backend API URL (Production)
REACT_APP_API_URL=https://your-backend-url.com/api

# Sentry DSN (Production)
REACT_APP_SENTRY_DSN=${REACT_APP_SENTRY_DSN}

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false

# Application Version
REACT_APP_VERSION=1.0.0
```

### How to Get Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Click the gear icon → Project Settings
4. Scroll down to "Your apps" section
5. Click on your web app or create one
6. Copy the configuration values

---

## Backend Environment Variables

### Development (.env)

Create `backend/.env` for local development:

```env
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# JWT Configuration
JWT_SECRET_KEY=dev-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
REFRESH_TOKEN_EXPIRATION_DAYS=7
SESSION_INACTIVITY_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Server Configuration
PORT=5000
HOST=0.0.0.0

# Email Configuration (disabled in development)
EMAIL_NOTIFICATIONS_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=admin@example.com

# Security Configuration
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
SESSION_TIMEOUT_MINUTES=30
MFA_LOCKOUT_ATTEMPTS=3
ENCRYPTION_KEY=dev-encryption-key-change-in-production

# Rate Limiting
RATE_LIMIT_ACCESS_REQUESTS=100/hour
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_API=1000/hour

# Request Size Limits
MAX_CONTENT_LENGTH_MB=1

# Audit Log Configuration
LOG_RETENTION_DAYS=90
```

### Production (.env.production)

Create `backend/.env.production` for production:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
REFRESH_TOKEN_EXPIRATION_DAYS=7
SESSION_INACTIVITY_MINUTES=30

# CORS Configuration (IMPORTANT: Set to your actual frontend URL)
CORS_ORIGINS=https://your-frontend-domain.com

# Server Configuration
PORT=${PORT}
HOST=0.0.0.0

# Email Configuration
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=${SMTP_PORT}
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
ALERT_EMAIL=${ALERT_EMAIL}

# Security Configuration
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
SESSION_TIMEOUT_MINUTES=30
MFA_LOCKOUT_ATTEMPTS=3
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Rate Limiting
RATE_LIMIT_ACCESS_REQUESTS=100/hour
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_API=1000/hour

# Redis URL for distributed rate limiting (optional)
# REDIS_URL=redis://localhost:6379/0

# Request Size Limits
MAX_CONTENT_LENGTH_MB=1

# TLS/HTTPS Configuration
PREFERRED_URL_SCHEME=https
SESSION_COOKIE_SECURE=true

# Audit Log Configuration
LOG_RETENTION_DAYS=90

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
APP_VERSION=1.0.0
```

---

## Generating Secure Secrets

### Using Python

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Using OpenSSL

```bash
# Generate SECRET_KEY
openssl rand -base64 32

# Generate JWT_SECRET_KEY
openssl rand -base64 32

# Generate ENCRYPTION_KEY
openssl rand -base64 32
```

### Using Node.js

```bash
# Generate secrets
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**IMPORTANT**: 
- Never commit these secrets to version control
- Use different secrets for development and production
- Store production secrets securely in your deployment platform

---

## Firebase Configuration

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add project"
3. Enter project name
4. Enable Google Analytics (optional)
5. Create project

### 2. Enable Authentication

1. In Firebase Console, go to Authentication
2. Click "Get started"
3. Enable "Email/Password" sign-in method
4. Save

### 3. Create Firestore Database

1. In Firebase Console, go to Firestore Database
2. Click "Create database"
3. Choose "Start in production mode"
4. Select location (choose closest to your users)
5. Create

### 4. Download Service Account Credentials

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save as `backend/firebase-credentials.json`
4. **NEVER commit this file to Git**

### 5. Get Web App Configuration

1. Go to Project Settings → General
2. Scroll to "Your apps"
3. Click "Add app" → Web
4. Register app
5. Copy configuration values to frontend `.env`

---

## Email Configuration

### Using Gmail

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to Google Account → Security
   - Under "Signing in to Google", select "App passwords"
   - Generate password for "Mail"
   - Copy the 16-character password

3. **Configure Environment Variables**:
```env
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
ALERT_EMAIL=admin@example.com
```

### Using SendGrid

```env
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
ALERT_EMAIL=admin@example.com
```

### Using AWS SES

```env
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_ses_smtp_username
SMTP_PASSWORD=your_ses_smtp_password
ALERT_EMAIL=admin@example.com
```

---

## Monitoring Configuration

### Sentry Setup

1. **Create Sentry Account**: [sentry.io](https://sentry.io)
2. **Create Projects**:
   - One for React (frontend)
   - One for Python/Flask (backend)
3. **Get DSN**: Copy from project settings
4. **Configure**:

Frontend:
```env
REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx
```

Backend:
```env
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Firebase Crashlytics (Alternative)

Already configured in Firebase project. No additional setup needed.

---

## Platform-Specific Setup

### Vercel

1. **Connect Repository**: Link GitHub/GitLab repo
2. **Set Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add all `REACT_APP_*` variables
   - Set for Production, Preview, and Development
3. **Deploy**: Push to main branch

### Render

1. **Create Web Service**: Connect repository
2. **Set Environment Variables**:
   - Go to Environment tab
   - Add all backend environment variables
   - Use "Generate Value" for secrets
3. **Add Secret Files**:
   - Add `firebase-credentials.json` as Secret File
4. **Deploy**: Push to main branch

### Google Cloud Run

1. **Set Environment Variables**:
```bash
gcloud run services update zero-trust-backend \
  --update-env-vars KEY1=VALUE1,KEY2=VALUE2
```

2. **Store Secrets in Secret Manager**:
```bash
# Create secret
echo -n "secret_value" | gcloud secrets create SECRET_NAME --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member=serviceAccount:SERVICE_ACCOUNT \
  --role=roles/secretmanager.secretAccessor

# Use in Cloud Run
gcloud run services update zero-trust-backend \
  --set-secrets=ENV_VAR=SECRET_NAME:latest
```

### Firebase Hosting

Environment variables are build-time only. Set in `.env.production` before building:

```bash
# Set variables
export REACT_APP_API_URL=https://your-backend.com/api

# Build
npm run build

# Deploy
firebase deploy --only hosting
```

---

## Security Best Practices

1. **Never commit secrets to Git**
   - Add `.env` to `.gitignore`
   - Add `firebase-credentials.json` to `.gitignore`

2. **Use different secrets for each environment**
   - Development secrets can be simpler
   - Production secrets must be cryptographically secure

3. **Rotate secrets regularly**
   - Change secrets every 90 days
   - Immediately rotate if compromised

4. **Limit access to production secrets**
   - Only authorized team members
   - Use deployment platform's secret management

5. **Use environment-specific configurations**
   - Don't use development credentials in production
   - Verify CORS_ORIGINS in production

6. **Monitor for exposed secrets**
   - Use tools like GitGuardian
   - Scan commits before pushing

---

## Verification

### Frontend

```bash
cd frontend
npm start

# Check console for:
# - No errors
# - Firebase initialized
# - API URL correct
```

### Backend

```bash
cd backend
python run.py

# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
# {"status": "healthy", "checks": {...}}
```

### Integration

```bash
# Test CORS
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS \
  http://localhost:5000/api/auth/verify

# Should return CORS headers
```

---

## Troubleshooting

### "Firebase not initialized"
- Check `REACT_APP_FIREBASE_*` variables are set
- Verify variable names start with `REACT_APP_`
- Restart development server after changing `.env`

### "CORS error"
- Verify `CORS_ORIGINS` includes frontend URL
- Check for trailing slashes (should not have)
- Ensure protocol matches (http vs https)

### "Firebase credentials not found"
- Check `firebase-credentials.json` exists in backend directory
- Verify `FIREBASE_CREDENTIALS_PATH` is correct
- Ensure file has proper JSON format

### "Email not sending"
- Verify SMTP credentials are correct
- Check `EMAIL_NOTIFICATIONS_ENABLED=true`
- Test SMTP connection manually
- Check firewall/security group settings

---

## Quick Reference

### Required Variables

**Frontend (Minimum)**:
- `REACT_APP_FIREBASE_API_KEY`
- `REACT_APP_FIREBASE_AUTH_DOMAIN`
- `REACT_APP_FIREBASE_PROJECT_ID`
- `REACT_APP_API_URL`

**Backend (Minimum)**:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`
- `CORS_ORIGINS`
- `FIREBASE_CREDENTIALS_PATH`

### Optional Variables

- `REACT_APP_SENTRY_DSN` - Error tracking
- `SENTRY_DSN` - Backend error tracking
- `EMAIL_NOTIFICATIONS_ENABLED` - Email alerts
- `REDIS_URL` - Distributed rate limiting

---

## Support

For issues with environment setup:
1. Check this guide thoroughly
2. Verify all required variables are set
3. Check deployment platform documentation
4. Review application logs for specific errors
