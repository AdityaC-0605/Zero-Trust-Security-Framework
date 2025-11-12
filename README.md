# Zero Trust Security Framework

A full-stack web application implementing continuous verification and policy-based access control for educational institutions.

## Project Structure

```
.
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services and Firebase integration
│   │   ├── contexts/        # React Context providers
│   │   ├── models/          # Data models and types
│   │   └── utils/           # Utility functions
│   ├── public/
│   └── package.json
│
├── backend/                  # Flask backend application
│   ├── app/
│   │   ├── services/        # Business logic services
│   │   ├── models/          # Data models
│   │   ├── routes/          # API endpoints
│   │   └── utils/           # Helper functions
│   ├── venv/                # Python virtual environment
│   ├── requirements.txt
│   └── run.py
│
└── .kiro/                    # Kiro specs and configuration
    └── specs/
        └── zero-trust-security-framework/
```

## Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Firebase account with Authentication and Firestore enabled

## Setup Instructions

### 1. Firebase Configuration

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firebase Authentication (Email/Password provider)
3. Enable Cloud Firestore
4. Download service account credentials:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save as `backend/firebase-credentials.json`
5. Get your Firebase web app configuration:
   - Go to Project Settings > General
   - Under "Your apps", select Web app
   - Copy the configuration values

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (already done during setup)
npm install

# Configure environment variables
cp .env.example .env
# Edit .env and add your Firebase configuration values

# Start development server
npm start
```

The frontend will run on `http://localhost:3000`

### 3. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (already done during setup)
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and update configuration values

# Ensure Firebase credentials are in place
# Copy your downloaded credentials to firebase-credentials.json

# Run the development server
python run.py
```

The backend will run on `http://localhost:5000`

## Environment Variables

### Frontend (.env)

- `REACT_APP_FIREBASE_API_KEY`: Firebase API key
- `REACT_APP_FIREBASE_AUTH_DOMAIN`: Firebase auth domain
- `REACT_APP_FIREBASE_PROJECT_ID`: Firebase project ID
- `REACT_APP_FIREBASE_STORAGE_BUCKET`: Firebase storage bucket
- `REACT_APP_FIREBASE_MESSAGING_SENDER_ID`: Firebase messaging sender ID
- `REACT_APP_FIREBASE_APP_ID`: Firebase app ID
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:5000/api)

### Backend (.env)

- `SECRET_KEY`: Flask secret key for session management
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account credentials
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:3000)
- `PORT`: Server port (default: 5000)

See `.env.example` files for complete configuration options.

## Technology Stack

### Frontend
- React 18.2+
- React Router v6
- Tailwind CSS
- Axios
- Firebase SDK

### Backend
- Flask 3.0+
- Flask-CORS
- Firebase Admin SDK
- PyJWT
- python-dotenv
- pyotp (for MFA)
- cryptography

### Database & Services
- Firebase Authentication
- Cloud Firestore

## Development

### Frontend Development

```bash
cd frontend
npm start          # Start development server
npm test           # Run tests
npm run build      # Build for production
```

### Backend Development

```bash
cd backend
source venv/bin/activate
python run.py      # Start development server
```

## Deployment

The application is ready for production deployment with support for multiple platforms.

### Deployment Options

**Recommended Stack**:
- **Frontend**: Vercel, Netlify, or Firebase Hosting
- **Backend**: Render, Google Cloud Run, or Google App Engine
- **Database**: Firebase Firestore (already configured)

### Automated Deployment

Use the deployment script for automated deployment:

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

### Platform-Specific Configuration

The project includes configuration files for various platforms:

- **Google Cloud**: `backend/app.yaml` and `backend/cloudbuild.yaml`
- **Render**: `backend/render.yaml`
- **Docker**: `backend/Dockerfile` and `backend/.dockerignore`
- **Firestore**: `backend/firestore.indexes.json` and `backend/firestore.rules`

### Firestore Deployment

Deploy Firestore rules and indexes:

```bash
cd backend
./deploy-firestore.sh
```

### Deployment Features

✅ Production-ready configuration files  
✅ Docker support for containerized deployment  
✅ Health check endpoints  
✅ Security headers and CORS configuration  
✅ SSL/TLS support  
✅ Firestore rules and indexes  

## Features

### Implemented

- ✅ User Authentication (Email/Password)
- ✅ Multi-Factor Authentication (MFA)
- ✅ Role-Based Access Control (Student, Faculty, Admin)
- ✅ Policy-Based Access Evaluation
- ✅ Intent Analysis
- ✅ Confidence Scoring
- ✅ Access Request Management
- ✅ Audit Logging
- ✅ User Management (Admin)
- ✅ Policy Configuration (Admin)
- ✅ Analytics and Reporting
- ✅ Real-Time Notifications
- ✅ Session Management
- ✅ Security Hardening
- ✅ Firestore Integration
- ✅ Seed Data and Default Policies
- ✅ Integration Tests
- ✅ Production Deployment Configuration

### Architecture

The application follows a three-tier architecture:

1. **Presentation Layer**: React SPA with Tailwind CSS
2. **Application Layer**: Flask REST API with business logic
3. **Data Layer**: Firebase Authentication + Firestore

For detailed architecture and design decisions, see `.kiro/specs/zero-trust-security-framework/design.md`.

## Testing

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

### Integration Tests

```bash
cd backend
source venv/bin/activate
pytest tests/
```

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health check
curl http://localhost:5000/api/health

# Production
curl https://your-backend-url.com/api/health
```

### Seed Data

Initialize the database with default policies and test data:

```bash
cd backend
source venv/bin/activate
python seed_data.py
```

### Logs

- **Frontend**: Browser console and Sentry (if configured)
- **Backend**: Application logs and Sentry (if configured)
- **Audit**: Firestore `auditLogs` collection

## Security

### Security Features

- HTTPS/TLS enforcement
- JWT token-based authentication
- HttpOnly, Secure, SameSite cookies
- CSRF protection
- Rate limiting
- Input sanitization
- XSS protection
- SQL injection prevention
- MFA support
- Account lockout after failed attempts
- Session timeout
- Comprehensive audit logging

### Security Best Practices

1. Never commit `.env` files or `firebase-credentials.json`
2. Use strong, unique secrets for production
3. Rotate secrets regularly (every 90 days)
4. Keep dependencies updated
5. Monitor security alerts
6. Review audit logs regularly
7. Use HTTPS in production
8. Configure CORS with specific origins (no wildcards)

## Documentation

- **Backend README**: `backend/README.md` - Backend-specific documentation
- **Design Document**: `.kiro/specs/zero-trust-security-framework/design.md`
- **Requirements**: `.kiro/specs/zero-trust-security-framework/requirements.md`
- **Tasks**: `.kiro/specs/zero-trust-security-framework/tasks.md`

## Support

For issues or questions:

1. Check the backend README (`backend/README.md`) for detailed setup instructions
2. Review application logs and health check endpoints
3. Check platform-specific documentation (Vercel, Render, Firebase, Google Cloud)
4. Review the design document for architecture details

## License

This project is part of an educational security framework implementation.
