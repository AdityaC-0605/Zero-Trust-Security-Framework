# Zero Trust Security Framework - Deployment Guide

This guide covers the complete deployment process for the Zero Trust Security Framework application, including frontend, backend, database, monitoring, and backup configuration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Frontend Deployment](#frontend-deployment)
4. [Backend Deployment](#backend-deployment)
5. [Database Configuration](#database-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Backup Configuration](#backup-configuration)
8. [Custom Domain & SSL](#custom-domain--ssl)
9. [Post-Deployment Verification](#post-deployment-verification)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- Firebase project (Authentication + Firestore)
- Vercel account (for frontend) OR Firebase Hosting
- Render account (for backend) OR Google Cloud Platform
- Sentry account (optional, for error tracking)
- Custom domain (optional)

### Required Tools
- Node.js 18+ and npm
- Python 3.11+
- Firebase CLI: `npm install -g firebase-tools`
- Vercel CLI (optional): `npm install -g vercel`
- gcloud CLI (for GCP deployment): [Install Guide](https://cloud.google.com/sdk/docs/install)

---

## Environment Setup

### 1. Firebase Project Setup

```bash
# Login to Firebase
firebase login

# Initialize Firebase in your project
cd frontend
firebase init

# Select:
# - Hosting
# - Firestore
# - Use existing project or create new one
```

### 2. Generate Secrets

```bash
# Generate secure secrets for production
python3 -c "import secrets; print(secrets.token_urlsafe(32))"  # SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"  # JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"  # ENCRYPTION_KEY
```

### 3. Download Firebase Credentials

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save as `backend/firebase-credentials.json`
4. **IMPORTANT**: Never commit this file to version control

---

## Frontend Deployment

### Option A: Vercel Deployment (Recommended)

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Configure Environment Variables

Create a `.env.production` file or set in Vercel dashboard:

```env
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id
REACT_APP_API_URL=https://your-backend-url.com/api
REACT_APP_SENTRY_DSN=your_sentry_dsn (optional)
```

#### 3. Deploy to Vercel

```bash
cd frontend

# First deployment (interactive)
vercel

# Production deployment
vercel --prod

# Or link to existing project
vercel link
vercel --prod
```

#### 4. Configure Environment Variables in Vercel Dashboard

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add all variables from `.env.production`
3. Redeploy: `vercel --prod`

### Option B: Firebase Hosting

#### 1. Build Production Bundle

```bash
cd frontend
npm run build
```

#### 2. Deploy to Firebase Hosting

```bash
firebase deploy --only hosting
```

#### 3. Set Environment Variables

Firebase Hosting doesn't support server-side environment variables. Use build-time variables:

```bash
# Create .env.production with your values
npm run build
firebase deploy --only hosting
```

---

## Backend Deployment

### Option A: Render Deployment (Recommended)

#### 1. Create Render Account

Sign up at [render.com](https://render.com)

#### 2. Create New Web Service

1. Connect your GitHub repository
2. Select the `backend` directory
3. Choose "Python" environment
4. Use the provided `render.yaml` configuration

#### 3. Configure Environment Variables

In Render Dashboard → Environment:

```env
FLASK_ENV=production
SECRET_KEY=<generated_secret>
JWT_SECRET_KEY=<generated_secret>
ENCRYPTION_KEY=<generated_secret>
CORS_ORIGINS=https://your-frontend-domain.com
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=admin@example.com
SENTRY_DSN=your_sentry_dsn (optional)
```

#### 4. Add Firebase Credentials

1. In Render Dashboard → Environment → Secret Files
2. Add file: `firebase-credentials.json`
3. Paste contents of your Firebase service account JSON

#### 5. Deploy

```bash
# Render auto-deploys on git push
git push origin main

# Or use Render CLI
render deploy
```

### Option B: Google Cloud Run

#### 1. Build and Push Docker Image

```bash
cd backend

# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/zero-trust-backend

# Or use Docker
docker build -t gcr.io/YOUR_PROJECT_ID/zero-trust-backend .
docker push gcr.io/YOUR_PROJECT_ID/zero-trust-backend
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy zero-trust-backend \
  --image gcr.io/YOUR_PROJECT_ID/zero-trust-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5000 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 1 \
  --timeout 120 \
  --set-env-vars FLASK_ENV=production \
  --set-secrets FIREBASE_CREDENTIALS=firebase-credentials:latest
```

#### 3. Set Environment Variables

```bash
gcloud run services update zero-trust-backend \
  --update-env-vars \
  SECRET_KEY=<secret>,\
  JWT_SECRET_KEY=<secret>,\
  ENCRYPTION_KEY=<secret>,\
  CORS_ORIGINS=https://your-frontend.com
```

#### 4. Store Firebase Credentials in Secret Manager

```bash
# Create secret
gcloud secrets create firebase-credentials \
  --data-file=firebase-credentials.json

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding firebase-credentials \
  --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
  --role=roles/secretmanager.secretAccessor
```

### Option C: Google App Engine

```bash
cd backend

# Deploy using app.yaml
gcloud app deploy

# Set environment variables
gcloud app deploy --set-env-vars KEY=VALUE
```

---

## Database Configuration

### 1. Firestore Security Rules

Deploy security rules:

```bash
cd backend
firebase deploy --only firestore:rules
```

### 2. Firestore Indexes

Deploy composite indexes:

```bash
firebase deploy --only firestore:indexes
```

### 3. Initialize Database

Run seed script to create default policies and system configuration:

```bash
# Local (development)
cd backend
python seed_data.py

# Production (via API)
curl -X POST https://your-backend-url.com/api/admin/seed \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Monitoring Setup

### Option A: Sentry (Recommended)

#### 1. Create Sentry Project

1. Sign up at [sentry.io](https://sentry.io)
2. Create new project for React (frontend)
3. Create new project for Python/Flask (backend)
4. Copy DSN for each project

#### 2. Install Sentry SDKs

```bash
# Frontend
cd frontend
npm install @sentry/react @sentry/tracing

# Backend
cd backend
pip install sentry-sdk
```

#### 3. Configure Sentry

Frontend - Add to `src/index.js`:

```javascript
import { initSentry } from './sentry.config';
initSentry();
```

Backend - Add to `run.py`:

```python
from monitoring import init_monitoring
init_monitoring(app)
```

#### 4. Set Environment Variables

```env
# Frontend
REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx

# Backend
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Option B: Firebase Crashlytics

Already configured in Firebase project. Errors automatically reported.

---

## Backup Configuration

### 1. Automated Firestore Backups

#### Using Google Cloud Scheduler

```bash
# Create backup bucket
gsutil mb gs://YOUR_PROJECT_ID-backups

# Create Cloud Scheduler job
gcloud scheduler jobs create http firestore-backup \
  --schedule="0 2 * * *" \
  --uri="https://firestore.googleapis.com/v1/projects/YOUR_PROJECT_ID/databases/(default):exportDocuments" \
  --http-method=POST \
  --message-body='{"outputUriPrefix":"gs://YOUR_PROJECT_ID-backups/firestore-backups"}' \
  --oauth-service-account-email=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --oauth-token-scope=https://www.googleapis.com/auth/datastore
```

#### Manual Backup

```bash
cd backend

# Export all collections
python backup_firestore.py export

# Backup to GCS
python backup_firestore.py backup

# Cleanup old backups (older than 90 days)
python backup_firestore.py cleanup 90
```

### 2. Backup Retention Policy

- Daily backups at 2 AM UTC
- Retain for 90 days
- Automatic cleanup of old backups
- Email notifications on failure

---

## Custom Domain & SSL

### Vercel Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate automatically provisioned

### Firebase Hosting Custom Domain

```bash
firebase hosting:channel:deploy production --only hosting
```

1. Go to Firebase Console → Hosting
2. Click "Add custom domain"
3. Follow DNS verification steps
4. SSL certificate automatically provisioned

### Render Custom Domain

1. Go to Render Dashboard → Your Service → Settings
2. Add custom domain under "Custom Domains"
3. Update DNS records (CNAME or A record)
4. SSL certificate automatically provisioned

### Cloud Run Custom Domain

```bash
gcloud run domain-mappings create \
  --service zero-trust-backend \
  --domain api.yourdomain.com \
  --region us-central1
```

---

## Post-Deployment Verification

### 1. Health Checks

```bash
# Backend health check
curl https://your-backend-url.com/api/health

# Expected response:
{
  "status": "healthy",
  "checks": {
    "database": {"status": "pass", "message": "Database connection OK"},
    "memory": {"status": "pass", "message": "Memory usage: 45%"}
  }
}
```

### 2. Frontend Verification

1. Visit your frontend URL
2. Test login functionality
3. Verify API connectivity
4. Check browser console for errors

### 3. Security Headers

```bash
curl -I https://your-frontend-url.com

# Verify headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000
```

### 4. CORS Configuration

```bash
curl -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS \
  https://your-backend-url.com/api/auth/verify
```

### 5. Test Critical Flows

- [ ] User registration and login
- [ ] MFA setup and verification
- [ ] Access request submission
- [ ] Admin user management
- [ ] Policy configuration
- [ ] Audit log viewing
- [ ] Real-time notifications

---

## Troubleshooting

### Frontend Issues

#### Build Fails

```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Environment Variables Not Loading

- Ensure variables start with `REACT_APP_`
- Rebuild after changing environment variables
- Check Vercel/Firebase dashboard for correct values

#### CORS Errors

- Verify `REACT_APP_API_URL` matches backend URL
- Check backend `CORS_ORIGINS` includes frontend URL
- Ensure no trailing slashes in URLs

### Backend Issues

#### Firebase Connection Fails

```bash
# Verify credentials file exists
ls -la backend/firebase-credentials.json

# Test Firebase connection
python -c "import firebase_admin; firebase_admin.initialize_app()"
```

#### Port Already in Use

```bash
# Find and kill process
lsof -ti:5000 | xargs kill -9
```

#### Memory Issues

- Increase memory allocation in deployment platform
- Check for memory leaks in application code
- Monitor with `psutil` or platform metrics

### Database Issues

#### Firestore Rules Blocking Requests

```bash
# Test rules locally
firebase emulators:start --only firestore

# Check rules in Firebase Console
# Ensure authenticated users have proper permissions
```

#### Missing Indexes

```bash
# Deploy indexes
firebase deploy --only firestore:indexes

# Check Firestore Console for index creation status
```

### Monitoring Issues

#### Sentry Not Receiving Events

- Verify DSN is correct
- Check `FLASK_ENV=production` (Sentry disabled in development)
- Test with manual error: `sentry_sdk.capture_exception(Exception("Test"))`

#### Health Check Failing

- Check database connectivity
- Verify Firebase credentials
- Review application logs

---

## Production Checklist

Before going live, verify:

- [ ] All environment variables set correctly
- [ ] Firebase credentials uploaded securely
- [ ] HTTPS/TLS enabled on all endpoints
- [ ] CORS configured with specific origins (no wildcards)
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Monitoring and error tracking active
- [ ] Automated backups scheduled
- [ ] Custom domain and SSL configured
- [ ] Health checks passing
- [ ] All critical flows tested
- [ ] Documentation updated
- [ ] Team trained on deployment process

---

## Maintenance

### Regular Tasks

- **Daily**: Monitor error rates and performance metrics
- **Weekly**: Review audit logs for security incidents
- **Monthly**: Verify backups and test restoration
- **Quarterly**: Update dependencies and security patches

### Scaling

#### Frontend
- Vercel/Firebase Hosting auto-scales
- Monitor bandwidth usage
- Optimize bundle size if needed

#### Backend
- Increase instance count in deployment platform
- Consider Redis for distributed rate limiting
- Monitor database query performance

### Updates

```bash
# Frontend updates
cd frontend
npm update
npm audit fix
npm run build
vercel --prod

# Backend updates
cd backend
pip list --outdated
pip install -U package_name
# Test thoroughly before deploying
git push origin main  # Auto-deploys on Render
```

---

## Support

For issues or questions:
- Check application logs in deployment platform
- Review Sentry error reports
- Consult Firebase Console for database issues
- Contact team lead or DevOps

---

## Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Sentry Documentation](https://docs.sentry.io)
