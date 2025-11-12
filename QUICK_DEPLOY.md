# Quick Deployment Guide

Get your Zero Trust Security Framework deployed in production in under 30 minutes.

## Prerequisites Checklist

- [ ] Firebase project created
- [ ] Vercel account (or Firebase Hosting)
- [ ] Render account (or Google Cloud)
- [ ] Git repository ready

## Step 1: Firebase Setup (5 minutes)

```bash
# 1. Create Firebase project at console.firebase.google.com
# 2. Enable Email/Password authentication
# 3. Create Firestore database
# 4. Download service account credentials → save as backend/firebase-credentials.json
```

## Step 2: Generate Secrets (1 minute)

```bash
# Generate three secrets and save them
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

## Step 3: Deploy Backend to Render (10 minutes)

1. **Sign up at [render.com](https://render.com)**

2. **Create New Web Service**
   - Connect your GitHub repository
   - Select `backend` directory
   - Choose Python environment

3. **Set Environment Variables** (in Render dashboard):
   ```
   FLASK_ENV=production
   SECRET_KEY=<from step 2>
   JWT_SECRET_KEY=<from step 2>
   ENCRYPTION_KEY=<from step 2>
   CORS_ORIGINS=https://your-app.vercel.app
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   ```

4. **Add Secret File**:
   - Go to Environment → Secret Files
   - Add `firebase-credentials.json`
   - Paste your Firebase credentials

5. **Deploy** - Render will auto-deploy

6. **Copy your backend URL** (e.g., `https://your-app.onrender.com`)

## Step 4: Deploy Frontend to Vercel (10 minutes)

1. **Sign up at [vercel.com](https://vercel.com)**

2. **Import Git Repository**
   - Click "New Project"
   - Import your repository
   - Set Root Directory to `frontend`

3. **Set Environment Variables**:
   ```
   REACT_APP_FIREBASE_API_KEY=<from Firebase console>
   REACT_APP_FIREBASE_AUTH_DOMAIN=<project-id>.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=<project-id>
   REACT_APP_FIREBASE_STORAGE_BUCKET=<project-id>.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=<from Firebase>
   REACT_APP_FIREBASE_APP_ID=<from Firebase>
   REACT_APP_API_URL=https://your-backend.onrender.com/api
   ```

4. **Deploy** - Click "Deploy"

5. **Copy your frontend URL** (e.g., `https://your-app.vercel.app`)

## Step 5: Update CORS (2 minutes)

1. Go back to Render dashboard
2. Update `CORS_ORIGINS` environment variable with your Vercel URL
3. Redeploy backend

## Step 6: Deploy Firestore Rules (2 minutes)

```bash
cd backend
firebase login
firebase init  # Select Firestore, use existing project
firebase deploy --only firestore:rules,firestore:indexes
```

## Step 7: Initialize Database (2 minutes)

```bash
cd backend
python seed_data.py
```

Or via API:
```bash
curl -X POST https://your-backend.onrender.com/api/admin/seed
```

## Step 8: Test Your Deployment (5 minutes)

1. **Visit your frontend URL**
2. **Create an account**
3. **Login**
4. **Submit an access request**
5. **Check it works!**

## Verification Checklist

- [ ] Frontend loads without errors
- [ ] Can create account
- [ ] Can login
- [ ] Can submit access request
- [ ] Dashboard displays correctly
- [ ] No CORS errors in console
- [ ] Backend health check passes: `curl https://your-backend.com/api/health`

## Common Issues

### CORS Error
**Problem**: "Access to fetch has been blocked by CORS policy"

**Solution**: 
1. Check `CORS_ORIGINS` in Render includes your Vercel URL
2. Ensure no trailing slash
3. Redeploy backend

### Firebase Error
**Problem**: "Firebase: Error (auth/configuration-not-found)"

**Solution**:
1. Verify all `REACT_APP_FIREBASE_*` variables are set in Vercel
2. Redeploy frontend

### Backend 500 Error
**Problem**: Backend returns 500 errors

**Solution**:
1. Check Render logs for errors
2. Verify `firebase-credentials.json` is uploaded as Secret File
3. Verify all required environment variables are set

## Next Steps

- [ ] Set up custom domain (optional)
- [ ] Configure email notifications
- [ ] Set up Sentry for error tracking
- [ ] Configure automated backups
- [ ] Review security settings

## Full Documentation

For detailed instructions, see:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Complete deployment guide
- [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) - Environment variables guide
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Comprehensive checklist

## Support

If you encounter issues:
1. Check Render logs: Dashboard → Logs
2. Check Vercel logs: Dashboard → Deployments → View Function Logs
3. Check browser console for frontend errors
4. Review [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section

---

**Estimated Total Time**: 30-40 minutes

**Cost**: 
- Firebase: Free tier (sufficient for development)
- Vercel: Free tier
- Render: Free tier (or $7/month for production)

**You're done!** 🎉

Your Zero Trust Security Framework is now live in production.
