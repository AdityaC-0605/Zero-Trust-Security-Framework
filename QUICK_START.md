# 🚀 Quick Start - Zero Trust Security Framework

## What You Need to Do Right Now

### 1️⃣ Get Firebase Web Config (5 minutes)

Go to: https://console.firebase.google.com/project/zero-trust-security-framework/settings/general

Look for the **firebaseConfig** object and copy these 3 values to `frontend/.env`:

```bash
REACT_APP_FIREBASE_API_KEY=AIzaSy...           # Copy from apiKey
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123...  # Copy from messagingSenderId
REACT_APP_FIREBASE_APP_ID=1:123...             # Copy from appId
```

### 2️⃣ Enable Firebase Services (2 minutes)

**Enable Authentication:**
- Firebase Console → Authentication → Get Started → Sign-in method
- Enable "Email/Password" → Save

**Enable Firestore:**
- Firebase Console → Firestore Database → Create database
- Start in test mode → Choose location → Enable

### 3️⃣ Install & Run (5 minutes)

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py          # Creates test users
python run.py                # Starts server on :5000

# Terminal 2 - Frontend
cd frontend
npm install
npm start                    # Opens browser on :3000
```

### 4️⃣ Login

**Admin:** admin@example.com / Admin123!
**Faculty:** faculty@example.com / Faculty123!
**Student:** student@example.com / Student123!

---

## ✅ What's Already Done

- ✅ Backend .env configured with secure keys
- ✅ Firebase service account credentials in place
- ✅ Project structure ready
- ✅ All code implemented

## ⚠️ What You Need to Complete

- [ ] Add 3 Firebase values to `frontend/.env` (Step 1)
- [ ] Enable Authentication in Firebase Console (Step 2)
- [ ] Enable Firestore in Firebase Console (Step 2)
- [ ] Run the commands in Step 3

---

## 🆘 Quick Troubleshooting

**Backend won't start?**
```bash
lsof -i :5000  # Check if port is in use
```

**Frontend won't start?**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Can't find Firebase config?**
- Firebase Console → Project Settings (gear icon) → Scroll to "Your apps"
- If no web app exists, click "Add app" → Web (</> icon)

---

See `SETUP_GUIDE.md` for detailed instructions.
