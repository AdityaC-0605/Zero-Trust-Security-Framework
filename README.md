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

## Next Steps

This is the initial project setup. The following features will be implemented in subsequent tasks:

1. Firebase Integration and Authentication Service
2. Authentication UI Components
3. Multi-Factor Authentication (MFA)
4. Context Providers and State Management
5. Protected Routes and Authorization
6. Policy Engine Core Logic
7. And more...

Refer to `.kiro/specs/zero-trust-security-framework/tasks.md` for the complete implementation plan.

## License

This project is part of an educational security framework implementation.
