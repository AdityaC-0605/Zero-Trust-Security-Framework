# 🚀 Quick Start Guide

## ⚠️ Important: Stop Existing Servers First

If you see "Address already in use" error, run this in your terminal:

```bash
# Stop all processes on port 5000
pkill -9 -f "python.*run.py"
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Or use the helper script
cd backend && ./stop_server.sh
```

---

## 🎯 Option 1: Core Features Only (Recommended for First Run)

**No Redis or RabbitMQ needed** - Perfect for testing the application quickly.

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate
python run.py
```

**Expected output:**
- Redis initialization error (this is OK - Redis is optional)
- Firebase initialized successfully
- Starting server with WebSocket support on 0.0.0.0:5000

### Terminal 2: Frontend
```bash
cd frontend
npm start
```

**Access the app:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- Health Check: http://localhost:5001/health

---

## 🚀 Option 2: Full Features (With AI Capabilities)

**Requires Redis and RabbitMQ** - For behavioral biometrics, threat prediction, etc.

### Step 1: Install Redis and RabbitMQ (if not installed)

**macOS:**
```bash
brew install redis rabbitmq
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server rabbitmq-server
```

### Step 2: Start Services

**Terminal 1: Redis**
```bash
redis-server
```

**Terminal 2: RabbitMQ**
```bash
rabbitmq-server
```

**Terminal 3: Celery Worker**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

**Terminal 4: Backend**
```bash
cd backend
source venv/bin/activate
python run.py
```

**Terminal 5: Frontend**
```bash
cd frontend
npm start
```

---

## 🔧 Troubleshooting

### "Address already in use" Error

**Problem:** Port 5000 is already in use

**Solution:**
```bash
# Kill all processes on port 5001
lsof -ti:5001 | xargs kill -9

# Or kill Python processes
pkill -9 -f "python.*run.py"

# Then restart the backend
cd backend && source venv/bin/activate && python run.py
```

### "Redis connection refused" Warning

**Problem:** Redis is not running

**Solution:**
- **Option A:** Start Redis: `redis-server`
- **Option B:** Ignore it - Core features work without Redis

### "Network Error" in Frontend

**Problem:** Backend is not running or wrong URL

**Solution:**
1. Check backend is running: `curl http://localhost:5001/health`
2. Check frontend `.env` has: `REACT_APP_API_URL=http://localhost:5001/api`
3. Restart both backend and frontend

### Frontend Won't Compile

**Problem:** Node modules or cache issues

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📝 Default Test Accounts

After running `python backend/seed_data.py`:

```
Admin:
- Email: admin@university.edu
- Password: Admin123!

Faculty:
- Email: faculty@university.edu  
- Password: Faculty123!

Student:
- Email: student@university.edu
- Password: Student123!
```

---

## ✅ Verification

### Check Backend is Running
```bash
curl http://localhost:5001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "message": "Zero Trust Security Framework API"
}
```

### Check Frontend is Running
Open browser to: http://localhost:3000

You should see the login page.

---

## 🎯 Next Steps

1. **First Time Setup:**
   - Visit http://localhost:3000/signup
   - Create an admin account
   - Or run seed data: `cd backend && python seed_data.py`

2. **Test the Application:**
   - Login with test account
   - Submit an access request
   - View admin dashboard
   - Check audit logs

3. **Enable AI Features:**
   - Start Redis and RabbitMQ
   - Update `backend/.env`: Set `BEHAVIORAL_TRACKING_ENABLED=true`
   - Update `frontend/.env`: Set `REACT_APP_BEHAVIORAL_TRACKING_ENABLED=true`
   - Restart both servers

---

## 📚 Documentation

- **README.md** - Complete project overview
- **PROJECT_COMPLETION_SUMMARY.md** - Feature details
- **COMPLETION_REPORT.md** - Recent fixes and status
- **backend/API_DOCUMENTATION.md** - API reference
- **backend/DEPLOYMENT_GUIDE.md** - Production deployment

---

## 🆘 Still Having Issues?

1. Check all environment variables are set correctly
2. Verify Firebase credentials exist: `backend/firebase-credentials.json`
3. Check Python version: `python3 --version` (should be 3.9+)
4. Check Node version: `node --version` (should be 16+)
5. Review error logs in terminal

---

**Status:** ✅ Ready to Run  
**Recommended:** Start with Option 1 (Core Features Only)

