# Deployment Configuration Files

This directory contains all configuration files needed for deploying the Zero Trust Security Framework to production.

## 📁 File Overview

### Frontend Deployment

| File | Purpose | Platform |
|------|---------|----------|
| `frontend/vercel.json` | Vercel deployment configuration | Vercel |
| `frontend/firebase.json` | Firebase Hosting configuration | Firebase |
| `frontend/.env.production` | Production environment variables | All |
| `frontend/sentry.config.js` | Error tracking configuration | Sentry |

### Backend Deployment

| File | Purpose | Platform |
|------|---------|----------|
| `backend/render.yaml` | Render deployment configuration | Render |
| `backend/Dockerfile` | Docker container configuration | Docker/Cloud Run |
| `backend/.dockerignore` | Docker build exclusions | Docker |
| `backend/cloudbuild.yaml` | Google Cloud Build configuration | GCP |
| `backend/app.yaml` | App Engine configuration | GCP App Engine |
| `backend/.env.production` | Production environment variables | All |
| `backend/production_config.py` | Production Flask configuration | All |
| `backend/monitoring.py` | Monitoring and error tracking | All |

### Backup & Maintenance

| File | Purpose |
|------|---------|
| `backend/backup_firestore.py` | Firestore backup script |
| `backend/backup_schedule.yaml` | Backup scheduling configuration |

### Documentation

| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | Complete deployment guide |
| `QUICK_DEPLOY.md` | Quick start deployment (30 min) |
| `ENVIRONMENT_SETUP.md` | Environment variables guide |
| `DEPLOYMENT_CHECKLIST.md` | Pre-deployment checklist |
| `deploy.sh` | Automated deployment script |

## 🚀 Quick Start

### Option 1: Automated Deployment

```bash
# Make script executable
chmod +x deploy.sh

# Deploy frontend only
./deploy.sh frontend

# Deploy backend only
./deploy.sh backend

# Deploy everything
./deploy.sh all
```

### Option 2: Manual Deployment

Follow the [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) guide for step-by-step instructions.

## 📋 Deployment Platforms

### Recommended Stack

- **Frontend**: Vercel (easiest) or Firebase Hosting
- **Backend**: Render (easiest) or Google Cloud Run
- **Database**: Firebase Firestore (already configured)
- **Monitoring**: Sentry (optional but recommended)

### Alternative Platforms

#### Frontend
- Netlify
- AWS Amplify
- Cloudflare Pages
- GitHub Pages (static only)

#### Backend
- Google App Engine
- AWS Elastic Beanstalk
- Heroku
- DigitalOcean App Platform
- Railway

## 🔧 Configuration Files Explained

### Frontend: vercel.json

Configures Vercel deployment with:
- Static file caching
- SPA routing (all routes → index.html)
- Security headers
- Environment variable references

### Frontend: firebase.json

Configures Firebase Hosting with:
- Build directory (`build`)
- Rewrites for SPA routing
- Cache control headers
- Security headers

### Backend: render.yaml

Configures Render deployment with:
- Python runtime
- Build and start commands
- Environment variables
- Health check endpoint
- Auto-scaling settings

### Backend: Dockerfile

Multi-stage Docker build:
- Stage 1: Install dependencies
- Stage 2: Production image
- Non-root user for security
- Health check configuration
- Gunicorn WSGI server

### Backend: cloudbuild.yaml

Google Cloud Build pipeline:
- Build Docker image
- Push to Container Registry
- Deploy to Cloud Run
- Configure resources and scaling

## 🔐 Security Considerations

### Secrets Management

**Never commit these files**:
- `.env` (any environment)
- `firebase-credentials.json`
- Any file containing API keys or passwords

**Use platform secret management**:
- Vercel: Environment Variables in dashboard
- Render: Environment Variables + Secret Files
- GCP: Secret Manager
- GitHub: Repository Secrets (for CI/CD)

### Environment Variables

**Required for Production**:
- `SECRET_KEY` - Flask session encryption
- `JWT_SECRET_KEY` - JWT token signing
- `ENCRYPTION_KEY` - MFA secret encryption
- `CORS_ORIGINS` - Allowed frontend origins (no wildcards!)

**Generate secure secrets**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Configuration

**Development**:
```env
CORS_ORIGINS=http://localhost:3000
```

**Production** (IMPORTANT):
```env
CORS_ORIGINS=https://your-actual-domain.com
```

Never use wildcards (`*`) in production!

## 📊 Monitoring Setup

### Sentry (Recommended)

1. Create account at [sentry.io](https://sentry.io)
2. Create two projects (React + Python)
3. Get DSN for each
4. Set environment variables:
   ```env
   REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx  # Frontend
   SENTRY_DSN=https://xxx@sentry.io/xxx            # Backend
   ```

### Health Checks

Backend health endpoint: `/api/health`

```bash
curl https://your-backend.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "pass", "message": "Database connection OK"},
    "memory": {"status": "pass", "message": "Memory usage: 45%"}
  }
}
```

## 💾 Backup Configuration

### Automated Backups

**Google Cloud Scheduler** (recommended):
```bash
gcloud scheduler jobs create http firestore-backup \
  --schedule="0 2 * * *" \
  --uri="https://firestore.googleapis.com/v1/projects/PROJECT_ID/databases/(default):exportDocuments" \
  --http-method=POST \
  --message-body='{"outputUriPrefix":"gs://PROJECT_ID-backups/firestore-backups"}'
```

**Manual Backup**:
```bash
cd backend
python backup_firestore.py backup
```

**Restore from Backup**:
```bash
python backup_firestore.py restore <collection_name> <backup_file>
```

### Backup Schedule

- **Frequency**: Daily at 2 AM UTC
- **Retention**: 90 days
- **Location**: Google Cloud Storage
- **Cleanup**: Automatic (old backups deleted)

## 🔄 CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: cd frontend && npm install && npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## 📈 Scaling Considerations

### Frontend Scaling

Vercel and Firebase Hosting auto-scale. No configuration needed.

**Optimization tips**:
- Enable code splitting
- Optimize images
- Use CDN for static assets
- Implement lazy loading

### Backend Scaling

**Render**:
- Upgrade to paid plan for auto-scaling
- Configure instance count in dashboard

**Cloud Run**:
- Auto-scales based on traffic
- Configure min/max instances:
  ```bash
  gcloud run services update SERVICE \
    --min-instances=1 \
    --max-instances=10
  ```

**Database Scaling**:
- Firestore auto-scales
- Monitor usage in Firebase Console
- Optimize queries with indexes

## 🐛 Troubleshooting

### Deployment Fails

**Check**:
1. All required environment variables set
2. Build succeeds locally
3. Dependencies installed correctly
4. Platform-specific logs

**Common fixes**:
```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build

# Backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Runtime Errors

**Check**:
1. Environment variables in production
2. Firebase credentials uploaded
3. CORS configuration
4. Database connectivity

**Debug**:
```bash
# Check backend logs
# Render: Dashboard → Logs
# Cloud Run: gcloud run services logs read SERVICE

# Check frontend logs
# Vercel: Dashboard → Deployments → Function Logs
# Browser: Developer Console
```

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Documentation](https://docs.docker.com)
- [Sentry Documentation](https://docs.sentry.io)

## 🆘 Support

For deployment issues:

1. **Check documentation**: Start with [DEPLOYMENT.md](./DEPLOYMENT.md)
2. **Review logs**: Check platform-specific logs
3. **Verify configuration**: Use [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
4. **Test locally**: Ensure it works in development
5. **Check status pages**: Verify platform status

## 📝 Maintenance

### Regular Tasks

- **Daily**: Monitor error rates and performance
- **Weekly**: Review logs and metrics
- **Monthly**: Update dependencies, verify backups
- **Quarterly**: Security audit, rotate secrets

### Updates

```bash
# Update frontend dependencies
cd frontend
npm update
npm audit fix

# Update backend dependencies
cd backend
pip list --outdated
pip install -U package_name

# Test thoroughly before deploying
npm test
pytest

# Deploy
./deploy.sh all
```

---

## 🎯 Next Steps

1. ✅ Review [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) for fastest deployment
2. ✅ Follow [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for comprehensive setup
3. ✅ Configure monitoring with Sentry
4. ✅ Set up automated backups
5. ✅ Configure custom domain (optional)
6. ✅ Enable email notifications
7. ✅ Perform security audit

**Ready to deploy?** Start with [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)!
