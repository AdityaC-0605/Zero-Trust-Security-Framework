# Deployment Checklist

Use this checklist to ensure all deployment steps are completed correctly.

## Pre-Deployment

### Firebase Setup
- [ ] Firebase project created
- [ ] Firebase Authentication enabled (Email/Password)
- [ ] Firestore database created
- [ ] Service account credentials downloaded
- [ ] Firebase CLI installed: `npm install -g firebase-tools`
- [ ] Logged into Firebase: `firebase login`

### Environment Variables Prepared
- [ ] SECRET_KEY generated (32+ characters)
- [ ] JWT_SECRET_KEY generated (32+ characters)
- [ ] ENCRYPTION_KEY generated (32+ characters)
- [ ] Firebase configuration values collected
- [ ] SMTP credentials obtained (if using email notifications)
- [ ] Sentry DSN obtained (if using Sentry)

### Code Repository
- [ ] All code committed to Git
- [ ] `.env` files added to `.gitignore`
- [ ] `firebase-credentials.json` added to `.gitignore`
- [ ] Repository pushed to GitHub/GitLab

---

## Frontend Deployment

### Vercel Deployment
- [ ] Vercel account created
- [ ] Vercel CLI installed: `npm install -g vercel`
- [ ] Repository connected to Vercel
- [ ] Environment variables set in Vercel dashboard:
  - [ ] REACT_APP_FIREBASE_API_KEY
  - [ ] REACT_APP_FIREBASE_AUTH_DOMAIN
  - [ ] REACT_APP_FIREBASE_PROJECT_ID
  - [ ] REACT_APP_FIREBASE_STORAGE_BUCKET
  - [ ] REACT_APP_FIREBASE_MESSAGING_SENDER_ID
  - [ ] REACT_APP_FIREBASE_APP_ID
  - [ ] REACT_APP_API_URL
  - [ ] REACT_APP_SENTRY_DSN (optional)
- [ ] Production build successful
- [ ] Deployed to Vercel: `vercel --prod`
- [ ] Frontend URL accessible

### OR Firebase Hosting Deployment
- [ ] Firebase initialized in frontend directory
- [ ] `firebase.json` configured
- [ ] Production build created: `npm run build`
- [ ] Deployed to Firebase: `firebase deploy --only hosting`
- [ ] Frontend URL accessible

---

## Backend Deployment

### Render Deployment
- [ ] Render account created
- [ ] New Web Service created
- [ ] Repository connected
- [ ] Environment variables set in Render dashboard:
  - [ ] FLASK_ENV=production
  - [ ] SECRET_KEY
  - [ ] JWT_SECRET_KEY
  - [ ] ENCRYPTION_KEY
  - [ ] CORS_ORIGINS (frontend URL)
  - [ ] FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
  - [ ] EMAIL_NOTIFICATIONS_ENABLED
  - [ ] SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
  - [ ] ALERT_EMAIL
  - [ ] SENTRY_DSN (optional)
- [ ] Firebase credentials uploaded as Secret File
- [ ] Service deployed successfully
- [ ] Backend URL accessible
- [ ] Health check passing: `/api/health`

### OR Google Cloud Run Deployment
- [ ] GCP project created
- [ ] gcloud CLI installed and configured
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Environment variables configured
- [ ] Firebase credentials stored in Secret Manager
- [ ] Service URL accessible
- [ ] Health check passing

---

## Database Configuration

### Firestore Setup
- [ ] Security rules deployed: `firebase deploy --only firestore:rules`
- [ ] Indexes deployed: `firebase deploy --only firestore:indexes`
- [ ] Seed data script executed
- [ ] Default policies created
- [ ] Test admin user created
- [ ] Database accessible from backend

---

## Monitoring & Error Tracking

### Sentry Setup (Optional)
- [ ] Sentry account created
- [ ] Frontend project created in Sentry
- [ ] Backend project created in Sentry
- [ ] Sentry SDK installed in frontend
- [ ] Sentry SDK installed in backend
- [ ] DSN configured in environment variables
- [ ] Test error sent and received

### Firebase Crashlytics (Alternative)
- [ ] Crashlytics enabled in Firebase Console
- [ ] SDK configured in application

---

## Backup Configuration

### Automated Backups
- [ ] Backup bucket created in GCS
- [ ] Cloud Scheduler job created for daily backups
- [ ] Backup script tested manually
- [ ] Retention policy configured (90 days)
- [ ] Backup notifications configured
- [ ] Test backup and restore performed

---

## Security Configuration

### SSL/TLS
- [ ] HTTPS enabled on frontend
- [ ] HTTPS enabled on backend
- [ ] SSL certificates auto-provisioned
- [ ] HTTP redirects to HTTPS

### Security Headers
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Strict-Transport-Security configured
- [ ] Content-Security-Policy configured
- [ ] Referrer-Policy configured

### CORS Configuration
- [ ] CORS_ORIGINS set to specific frontend URL (no wildcards)
- [ ] Preflight requests working
- [ ] Credentials allowed for authenticated requests

### Rate Limiting
- [ ] Rate limits configured in backend
- [ ] Rate limiting tested
- [ ] 429 responses handled in frontend

---

## Custom Domain (Optional)

### Frontend Domain
- [ ] Custom domain purchased
- [ ] DNS records configured
- [ ] Domain added to Vercel/Firebase
- [ ] SSL certificate provisioned
- [ ] Domain accessible

### Backend Domain
- [ ] API subdomain configured (e.g., api.yourdomain.com)
- [ ] DNS records configured
- [ ] Domain added to Render/Cloud Run
- [ ] SSL certificate provisioned
- [ ] API accessible via custom domain
- [ ] Frontend updated with new API URL

---

## Testing & Verification

### Functionality Tests
- [ ] User registration works
- [ ] User login works
- [ ] MFA setup works
- [ ] MFA verification works
- [ ] Access request submission works
- [ ] Access request evaluation works
- [ ] Request history displays correctly
- [ ] Admin user management works
- [ ] Policy configuration works
- [ ] Audit logs display correctly
- [ ] Analytics display correctly
- [ ] Real-time notifications work
- [ ] Session timeout works
- [ ] Logout works

### Performance Tests
- [ ] Page load time < 3 seconds
- [ ] API response time < 2 seconds
- [ ] Dashboard loads within 2 seconds
- [ ] No console errors in browser
- [ ] No 500 errors in backend logs

### Security Tests
- [ ] Unauthenticated users redirected to login
- [ ] Unauthorized users see 403 errors
- [ ] JWT tokens expire after 60 minutes
- [ ] Session timeout after 30 minutes inactivity
- [ ] Failed login attempts tracked
- [ ] Account lockout after 5 failed attempts
- [ ] MFA required for sensitive operations
- [ ] CSRF protection working
- [ ] XSS protection working
- [ ] SQL injection protection working

### Integration Tests
- [ ] Frontend connects to backend
- [ ] Backend connects to Firestore
- [ ] Email notifications sent (if enabled)
- [ ] Error tracking reports errors
- [ ] Backups running successfully

---

## Documentation

- [ ] Deployment guide reviewed
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Admin credentials documented (securely)
- [ ] Backup/restore procedures documented
- [ ] Troubleshooting guide reviewed
- [ ] Team trained on deployment process

---

## Post-Deployment

### Monitoring
- [ ] Set up alerts for error rates
- [ ] Set up alerts for high response times
- [ ] Set up alerts for failed backups
- [ ] Monitor resource usage (CPU, memory, bandwidth)
- [ ] Review logs daily for first week

### Maintenance Schedule
- [ ] Daily: Check error rates and performance
- [ ] Weekly: Review audit logs
- [ ] Monthly: Verify backups and test restore
- [ ] Quarterly: Update dependencies

---

## Rollback Plan

In case of critical issues:

1. **Frontend Rollback**
   - Vercel: Revert to previous deployment in dashboard
   - Firebase: `firebase hosting:rollback`

2. **Backend Rollback**
   - Render: Revert to previous deployment in dashboard
   - Cloud Run: Deploy previous image version

3. **Database Rollback**
   - Restore from most recent backup
   - Run: `python backup_firestore.py restore <collection> <backup_file>`

---

## Sign-Off

- [ ] Development team lead approval
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for production

**Deployed By:** ___________________  
**Date:** ___________________  
**Version:** ___________________  
**Frontend URL:** ___________________  
**Backend URL:** ___________________  

---

## Notes

Use this section to document any deployment-specific notes, issues encountered, or deviations from the standard process:

```
[Add notes here]
```
