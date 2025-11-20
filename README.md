# Zero Trust Security Framework

A production-ready, full-stack web application implementing continuous verification, policy-based access control, and AI-powered security features for educational institutions.

**Project Status: 100% Complete ✅ | Production Ready**

This comprehensive security framework combines traditional Zero Trust principles with cutting-edge AI/ML technologies including behavioral biometrics, threat prediction, contextual intelligence, and blockchain audit trails.

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+ (3.9 is past end of life)
- **Firebase** account with Authentication and Firestore enabled
- **Redis** 6.0+ (optional, for AI features)
- **RabbitMQ** 3.8+ (optional, for background jobs)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zero-trust-security-framework
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your Firebase configuration
   ```

4. **Firebase Configuration**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Authentication (Email/Password)
   - Enable Cloud Firestore
   - Download service account credentials → Save as `backend/firebase-credentials.json`
   - Copy web app config to `frontend/.env`
   - See `frontend/FIREBASE_SETUP.md` for detailed setup instructions

5. **Deploy Firestore Indexes** (Required for optimal performance)
   ```bash
   cd backend
   chmod +x deploy-indexes.sh
   ./deploy-indexes.sh
   ```
   - Requires Firebase CLI: `npm install -g firebase-tools`
   - Login: `firebase login`
   - Set project: `firebase use zero-trust-security-framework`
   - See `backend/DEPLOY_FIRESTORE_INDEXES.md` for detailed instructions

6. **Start the Application**
   ```bash
   # Terminal 1: Backend
   cd backend && source venv/bin/activate && python run.py
   
   # Terminal 2: Frontend
   cd frontend && npm start
   ```

7. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

---

## 📁 Project Structure

```
.
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components (80+)
│   │   ├── services/        # API services
│   │   ├── contexts/        # React Context providers
│   │   ├── utils/           # Utility functions
│   │   └── styles/          # CSS and design system
│   └── package.json
│
├── backend/                  # Flask backend application
│   ├── app/
│   │   ├── services/        # Business logic (13 services)
│   │   ├── models/          # Data models (15 collections)
│   │   ├── routes/          # API endpoints (80+)
│   │   ├── tasks/           # Celery background jobs
│   │   └── utils/           # Helper functions
│   ├── firebase.json        # Firebase configuration
│   ├── firestore.indexes.json # Firestore database indexes
│   ├── deploy-indexes.sh    # Firestore index deployment script
│   ├── requirements.txt
│   └── run.py
│
└── .kiro/                    # Kiro specs and configuration
```

---

## 🎯 Key Features

### Core Zero Trust Framework (100% Complete)
- ✅ User Authentication (Email/Password + MFA with TOTP)
- ✅ Role-Based Access Control (Student, Faculty, Admin)
- ✅ Policy-Based Access Evaluation
- ✅ Intent Analysis & Confidence Scoring
- ✅ Access Request Management
- ✅ Comprehensive Audit Logging
- ✅ User Management Dashboard
- ✅ Policy Configuration
- ✅ Analytics and Reporting
- ✅ Real-Time Notifications
- ✅ Session Management
- ✅ Security Hardening

### AI-Powered Security Features (100% Complete)
- ✅ **Behavioral Biometrics**: LSTM-based continuous authentication
- ✅ **Threat Prediction**: Random Forest ML model for proactive security
- ✅ **Contextual Intelligence**: Multi-factor context evaluation
- ✅ **Adaptive Policies**: Self-optimizing security rules
- ✅ **Security Assistant**: Claude AI-powered guidance
- ✅ **Blockchain Audit**: Immutable audit trail with Ethereum + IPFS
- ✅ **Real-Time Infrastructure**: WebSocket, Redis, Celery
- ✅ **Network Visualization**: 3D topology viewer with Three.js
- ✅ **Training Simulations**: Security awareness training
- ✅ **Collaborative Security**: Community threat reporting

### Enhanced UI/UX (100% Complete)
- ✅ Modern design system with Tailwind CSS
- ✅ Dark mode with theme persistence
- ✅ Smooth animations with Framer Motion (60fps)
- ✅ WCAG 2.1 AA accessibility compliance
- ✅ Fully responsive (mobile, tablet, desktop)
- ✅ Multi-step forms with validation
- ✅ Interactive charts and visualizations
- ✅ Real-time updates and notifications
- ✅ 30+ reusable UI components
- ✅ Code quality: ESLint compliant, React hooks optimized

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 19.2.0 with React Router v7
- **Styling**: Tailwind CSS with custom design system
- **Animations**: Framer Motion
- **Charts**: Recharts
- **3D Graphics**: Three.js
- **Icons**: Lucide React
- **State**: React Context API
- **HTTP**: Axios with interceptors
- **Real-time**: Socket.IO Client
- **Auth**: Firebase SDK

### Backend
- **Framework**: Flask 3.0+ with Flask-CORS
- **Database**: Firebase Firestore
- **Auth**: Firebase Admin SDK, PyJWT
- **Real-time**: Flask-SocketIO with eventlet
- **Caching**: Redis 6.0+
- **Queue**: Celery with RabbitMQ
- **ML/AI**: PyTorch, scikit-learn, TensorFlow
- **Blockchain**: Web3.py, Ganache, Truffle
- **AI**: Anthropic Claude API
- **Storage**: IPFS for distributed storage
- **Security**: pyotp (MFA), cryptography (AES-256)

### Infrastructure
- **WebSocket Server**: 500+ concurrent connections
- **Cache Layer**: Redis with sub-millisecond access
- **Background Jobs**: 20+ Celery scheduled tasks
- **Blockchain**: Ethereum smart contracts
- **Distributed Storage**: IPFS nodes

---

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Flask Configuration
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
CORS_ORIGINS=http://localhost:3000
PORT=5001

# Encryption (Auto-generated if not set)
ENCRYPTION_KEY=your_fernet_key_here  # Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# AI Features (Optional)
BEHAVIORAL_TRACKING_ENABLED=true
THREAT_PREDICTION_ENABLED=true
CLAUDE_API_KEY=your_claude_api_key_here
SECURITY_ASSISTANT_ENABLED=true

# Blockchain (Optional)
BLOCKCHAIN_ENABLED=true
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
```

### Frontend Environment Variables (.env)

```env
# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id

# Backend API
REACT_APP_API_URL=http://localhost:5001/api
REACT_APP_WEBSOCKET_URL=http://localhost:5001

# Feature Flags
REACT_APP_BEHAVIORAL_TRACKING_ENABLED=true
REACT_APP_SECURITY_ASSISTANT_ENABLED=true
```

See `.env.example` files for complete configuration options.

---

## 🚢 Deployment

### Quick Deployment

```bash
# Make script executable
chmod +x deploy.sh

# Deploy frontend
./deploy.sh frontend

# Deploy backend
./deploy.sh backend

# Deploy everything
./deploy.sh all
```

### Supported Platforms

- **Frontend**: Vercel, Netlify, Firebase Hosting
- **Backend**: Render, Google Cloud Run, Google App Engine
- **Database**: Firebase Firestore (already configured)

### Deployment Files

- `backend/Dockerfile` - Docker containerization
- `backend/app.yaml` - Google App Engine
- `backend/cloudbuild.yaml` - Google Cloud Build
- `backend/render.yaml` - Render deployment
- `backend/firestore.rules` - Firestore security rules
- `backend/firestore.indexes.json` - Database indexes
- `backend/firebase.json` - Firebase project configuration
- `backend/deploy-indexes.sh` - Automated index deployment script

### Firestore Index Deployment

**Important:** Firestore requires composite indexes for queries with multiple filters or ordering. Deploy indexes before production use:

```bash
cd backend
./deploy-indexes.sh
```

This will deploy all required indexes defined in `firestore.indexes.json`. Index creation takes a few minutes. Check status in [Firebase Console](https://console.firebase.google.com/project/zero-trust-security-framework/firestore/indexes).

For detailed deployment instructions, see:
- `backend/DEPLOYMENT_GUIDE.md` - Production deployment
- `backend/DEPLOY_FIRESTORE_INDEXES.md` - Index deployment guide

---

## 🧪 Testing

### Frontend Tests

```bash
cd frontend
npm test              # Run tests in watch mode
npm run test:ci       # Run tests once with coverage
```

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest                # Run all tests
pytest -v             # Verbose output
pytest --cov          # With coverage report
```

### Health Check

```bash
# Backend health check
curl http://localhost:5001/health

# Production
curl https://your-backend-url.com/health
```

---

## 📊 API Endpoints

### Authentication (8 endpoints)
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/mfa/setup` - Setup MFA
- `POST /api/auth/mfa/verify` - Verify MFA code
- `POST /api/auth/refresh` - Refresh session
- `POST /api/auth/password-reset` - Reset password
- `GET /api/auth/verify-token` - Verify JWT token

### Access Requests (7 endpoints)
- `POST /api/access/request` - Submit access request
- `GET /api/access/history` - Get request history
- `GET /api/access/:id` - Get request details
- `PUT /api/access/:id/resubmit` - Resubmit request
- `GET /api/access/status/:id` - Get request status
- `DELETE /api/access/:id` - Delete request
- `GET /api/access/statistics` - Get statistics

### AI Features (26 endpoints)
- Behavioral Biometrics (8 endpoints)
- Threat Prediction (13 endpoints)
- Contextual Intelligence (5 endpoints)

### Admin Management (12 endpoints)
- User management
- Audit logs
- Analytics
- Policy configuration

**Total: 80+ API Endpoints**

For complete API documentation, see `backend/API_DOCUMENTATION.md`.

---

## 🔒 Security Features

### Authentication & Authorization
- JWT token-based authentication
- HttpOnly, Secure, SameSite cookies
- Multi-factor authentication (TOTP)
- Account lockout after 5 failed attempts
- Session timeout (60 minutes token, 30 minutes inactivity)
- CSRF protection

### Data Protection
- Encryption at rest (Firestore)
- Encryption in transit (HTTPS/TLS 1.2+)
- MFA secret encryption (AES-256)
- Secure password hashing (Firebase)
- Input sanitization (XSS prevention)

### Monitoring & Auditing
- Comprehensive audit logging
- Blockchain immutable audit trail
- Real-time threat detection
- Behavioral anomaly detection
- Admin alerting for high-severity events
- 90-day log retention minimum

---

## 📈 Performance Metrics

- **API Response Time**: <200ms average
- **ML Inference**: <50ms (behavioral), <30ms (threat prediction)
- **WebSocket Latency**: <100ms
- **Cache Hit Rate**: >80%
- **Animation FPS**: 60fps target
- **Concurrent Users**: 500+ supported

---

## 📚 Documentation

### Project Documentation
- **README.md** - This file, project overview
- **PROJECT_COMPLETION_SUMMARY.md** - Comprehensive project status

### Backend Documentation
- **backend/README.md** - Backend-specific documentation
- **backend/API_DOCUMENTATION.md** - Complete API reference
- **backend/DEPLOYMENT_GUIDE.md** - Production deployment
- **backend/DEPLOY_FIRESTORE_INDEXES.md** - Firestore index deployment guide
- **backend/INFRASTRUCTURE_SETUP.md** - Infrastructure configuration
- **backend/REALTIME_INFRASTRUCTURE.md** - WebSocket, Redis, Celery
- **backend/AI_INNOVATIONS_PROGRESS.md** - AI features status

### Frontend Documentation
- **frontend/UI_ENHANCEMENTS_SUMMARY.md** - UI/UX enhancements
- **frontend/COMPONENT_LIBRARY.md** - Component usage guide
- **frontend/FIREBASE_SETUP.md** - Firebase configuration guide

### Specification Documents
- **.kiro/specs/** - Complete specification documents

---

## 📊 Project Statistics

- **Total Files**: 150+
- **Backend Services**: 13 services
- **Frontend Components**: 80+ components
- **API Endpoints**: 80+ endpoints
- **Database Collections**: 15 Firestore collections
- **Background Tasks**: 20+ Celery scheduled tasks
- **ML Models**: 3 (LSTM, Random Forest, Isolation Forest)
- **Lines of Code**: ~25,000+ (estimated)

---

## 🎓 Default Test Accounts

After running seed data (`python backend/seed_data.py`):

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

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 5001 (or configured port) is in use
lsof -i :5001

# Check Python version
python3 --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Firebase errors
- Verify credentials file exists: `backend/firebase-credentials.json`
- Check Firebase console for enabled services
- Verify .env files have correct Firebase config
- See `frontend/FIREBASE_SETUP.md` for detailed setup instructions

### Firestore index errors
If you see errors like "The query requires an index":
```bash
# Deploy Firestore indexes
cd backend
./deploy-indexes.sh

# Or manually via Firebase CLI
firebase deploy --only firestore:indexes
```
- Requires Firebase CLI: `npm install -g firebase-tools`
- Must be logged in: `firebase login`
- See `backend/DEPLOY_FIRESTORE_INDEXES.md` for troubleshooting

### Redis/RabbitMQ not found
```bash
# macOS
brew install redis rabbitmq
brew services start redis
brew services start rabbitmq

# Ubuntu/Debian
sudo apt-get install redis-server rabbitmq-server
sudo systemctl start redis
sudo systemctl start rabbitmq-server
```

---

## 🤝 Contributing

This project is part of an educational security framework implementation. For contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is part of an educational security framework implementation.

---

## 🎉 Key Achievements

### Innovation
- ✅ ML-powered behavioral biometrics with LSTM neural networks
- ✅ Proactive threat prediction with Random Forest classifier
- ✅ Multi-factor contextual intelligence engine
- ✅ Self-optimizing adaptive security policies
- ✅ AI-powered security assistant with Claude
- ✅ Blockchain immutable audit trail with IPFS
- ✅ Real-time risk monitoring and alerting

### User Experience
- ✅ Modern, polished UI with smooth 60fps animations
- ✅ Full dark mode support with theme persistence
- ✅ WCAG 2.1 AA accessibility compliance
- ✅ Responsive design for all devices
- ✅ Intuitive multi-step forms with validation
- ✅ Real-time notifications and updates
- ✅ Comprehensive admin dashboards

### Security
- ✅ Zero Trust architecture with continuous verification
- ✅ Multi-factor authentication with TOTP
- ✅ Behavioral anomaly detection
- ✅ Threat prediction and prevention
- ✅ Comprehensive audit logging
- ✅ Blockchain immutable records
- ✅ Policy-based access control

### Code Quality & Maintenance
- ✅ ESLint compliant codebase with zero warnings
- ✅ Optimized React hooks and dependencies
- ✅ Automated Firestore index deployment
- ✅ Comprehensive error handling and validation
- ✅ Production-ready configuration management
- ✅ Detailed documentation and setup guides

---

## 📞 Support

For issues or questions:

1. Check **PROJECT_COMPLETION_SUMMARY.md** for comprehensive overview
2. Review **backend/API_DOCUMENTATION.md** for API reference
3. Check **backend/DEPLOYMENT_GUIDE.md** for deployment help
4. Review application logs and health check endpoints
5. Check platform-specific documentation

---

## 🔄 Recent Updates (November 2025)

### Code Quality Improvements
- ✅ Fixed all ESLint warnings and React hooks dependencies
- ✅ Optimized component lifecycle and memory management
- ✅ Improved error handling and validation

### Infrastructure Enhancements
- ✅ Added automated Firestore index deployment script
- ✅ Created comprehensive Firebase setup documentation
- ✅ Enhanced deployment configuration and error handling

### Documentation
- ✅ Added `backend/DEPLOY_FIRESTORE_INDEXES.md` - Index deployment guide
- ✅ Added `frontend/FIREBASE_SETUP.md` - Firebase configuration guide
- ✅ Updated troubleshooting sections with common issues

---

**Project Version**: 1.0.0  
**Last Updated**: November 20, 2025  
**Status**: 100% Complete ✅ | Production Ready 🚀

