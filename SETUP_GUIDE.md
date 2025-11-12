# Zero Trust Security Framework - Complete Setup Guide

## 🎯 Quick Start Checklist

- [x] Backend .env configured with secure keys
- [x] Firebase service account credentials in place
- [ ] Frontend Firebase web config (need to complete)
- [ ] Install backend dependencies
- [ ] Install frontend dependencies
- [ ] Initialize database with seed data
- [ ] Start backend server
- [ ] Start frontend server

---

## Step 1: Complete Firebase Configuration ⚠️

You need to get your Firebase **Web App** configuration values.

### How to Get Firebase Web Config:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **zero-trust-security-framework**
3. Click the gear icon ⚙️ > **Project Settings**
4. Scroll down to **Your apps** section
5. If you don't have a web app yet:
   - Click **Add app** > Select **Web** (</> icon)
   - Register app with nickname: "Zero Trust Web App"
   - You'll see the Firebase configuration object
6. If you already have a web app:
   - Click on your web app
   - Look for the `firebaseConfig` object

### Copy These Values to `frontend/.env`:

```javascript
// You'll see something like this in Firebase Console:
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "zero-trust-security-framework.firebaseapp.com",
  projectId: "zero-trust-security-framework",
  storageBucket: "zero-trust-security-framework.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
};
```

**Update `frontend/.env` with these values:**
- `REACT_APP_FIREBASE_API_KEY` = apiKey
- `REACT_APP_FIREBASE_MESSAGING_SENDER_ID` = messagingSenderId
- `REACT_APP_FIREBASE_APP_ID` = appId

---

## Step 2: Enable Firebase Services

### Enable Authentication:
1. In Firebase Console, go to **Authentication**
2. Click **Get Started**
3. Go to **Sign-in method** tab
4. Enable **Email/Password** provider
5. Click **Save**

### Enable Firestore:
1. In Firebase Console, go to **Firestore Database**
2. Click **Create database**
3. Choose **Start in test mode** (we'll deploy rules later)
4. Select a location (choose closest to your users)
5. Click **Enable**

---

## Step 3: Install Backend Dependencies

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4: Install Frontend Dependencies

```bash
cd frontend

# Install dependencies
npm install
```

---

## Step 5: Initialize Database with Seed Data

This creates default policies and test users.

```bash
cd backend
source venv/bin/activate
python seed_data.py
```

**Default Test Users Created:**
- **Admin**: admin@example.com / Admin123!
- **Faculty**: faculty@example.com / Faculty123!
- **Student**: student@example.com / Student123!

---

## Step 6: Start the Backend Server

```bash
cd backend
source venv/bin/activate
python run.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

**Test the backend:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-12T..."
}
```

---

## Step 7: Start the Frontend Server

Open a **new terminal window**:

```bash
cd frontend
npm start
```

The app will open at: **http://localhost:3000**

---

## 🎉 You're Ready!

### Login with Test Accounts:

1. **Admin Account**
   - Email: admin@example.com
   - Password: Admin123!
   - Access: Full system access, user management, policy configuration

2. **Faculty Account**
   - Email: faculty@example.com
   - Password: Faculty123!
   - Access: Course materials, student data, grading

3. **Student Account**
   - Email: student@example.com
   - Password: Student123!
   - Access: Course enrollment, assignments, grades

---

## 🔍 Verify Everything Works

### Backend Health Check:
```bash
curl http://localhost:5000/api/health
```

### Frontend Access:
- Open http://localhost:3000
- You should see the login page
- Try logging in with any test account

### Check Firestore:
1. Go to Firebase Console > Firestore Database
2. You should see collections: `users`, `policies`, `accessRequests`, `auditLogs`

---

## 🛠️ Troubleshooting

### Backend won't start:
- Check if port 5000 is available: `lsof -i :5000`
- Verify virtual environment is activated
- Check `backend/.env` has all required values
- Verify `firebase-credentials.json` exists

### Frontend won't start:
- Check if port 3000 is available: `lsof -i :3000`
- Run `npm install` again
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

### Firebase errors:
- Verify Firebase web config in `frontend/.env`
- Check Authentication is enabled in Firebase Console
- Check Firestore is created and accessible
- Verify service account credentials are valid

### Can't login:
- Run seed data script: `python seed_data.py`
- Check Firebase Console > Authentication > Users
- Check browser console for errors
- Verify backend is running on port 5000

---

## 📝 Current Configuration Status

### ✅ Backend (.env) - CONFIGURED
- Flask secret keys: Generated and set
- JWT secret: Generated and set
- Encryption key: Generated and set
- Firebase credentials: In place
- CORS: Configured for localhost:3000
- All security settings: Default values set

### ⚠️ Frontend (.env) - NEEDS COMPLETION
- Project ID: ✅ Set (zero-trust-security-framework)
- Auth Domain: ✅ Set
- Storage Bucket: ✅ Set
- API Key: ❌ Need from Firebase Console
- Messaging Sender ID: ❌ Need from Firebase Console
- App ID: ❌ Need from Firebase Console
- Backend API URL: ✅ Set (http://localhost:5000/api)

---

## 🔐 Security Notes

- The generated secret keys are for **development only**
- For production, generate new keys and store them securely
- Never commit `.env` files or `firebase-credentials.json` to git
- Change default test user passwords before deploying

---

## 📚 Next Steps

After getting the app running:

1. **Explore the Features**
   - Try different user roles
   - Create access requests
   - View audit logs (admin)
   - Configure policies (admin)

2. **Deploy Firestore Rules**
   ```bash
   cd backend
   ./deploy-firestore.sh
   ```

3. **Run Tests**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

4. **Read the Documentation**
   - Backend README: `backend/README.md`
   - Design Document: `.kiro/specs/zero-trust-security-framework/design.md`

---

## 🆘 Need Help?

Check these files for more details:
- `README.md` - Main project documentation
- `backend/README.md` - Backend-specific details
- `.kiro/specs/zero-trust-security-framework/` - Design and requirements

---

**Last Updated:** November 12, 2024
