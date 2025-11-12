# Backend - Zero Trust Security Framework

Flask backend API for the Zero Trust Security Framework.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Populate seed data (development only)
python seed_data.py

# Start server
python run.py
```

## Project Structure

```
backend/
├── app/
│   ├── models/              # Data models (User, Policy, AccessRequest, etc.)
│   ├── services/            # Business logic (PolicyEngine, IntentAnalyzer, etc.)
│   ├── routes/              # API endpoints
│   ├── middleware/          # Security middleware (CSRF, Authorization, etc.)
│   ├── tasks/               # Background tasks
│   └── utils/               # Utility functions
├── venv/                    # Python virtual environment
├── seed_data.py             # Seed data population script
├── test_seed_data.py        # Seed data validation tests
├── check_seed_data.py       # Check if seed data exists
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── firebase-credentials.json # Firebase service account (not in repo)
```

## Seed Data

The seed data script populates the database with test users, default policies, and sample data for development and testing.

### Quick Seed Commands

```bash
# Populate seed data
python seed_data.py

# Validate seed data (without Firebase)
python test_seed_data.py

# Check if seed data exists
python check_seed_data.py
```

### Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | student@test.edu | Student123! |
| Faculty | faculty@test.edu | Faculty123! |
| Admin | admin@test.edu | Admin123! |

**Note:** Users must also be created in Firebase Authentication before they can log in.

### What Gets Created

- ✓ 3 test user accounts (student, faculty, admin)
- ✓ 5 default access policies
- ✓ System configuration with thresholds
- ✓ Keyword categories for intent analysis
- ✓ 6 sample access requests
- ✓ Documentation (SEED_DATA_CREDENTIALS.md)

### Documentation

- `SEED_DATA_README.md` - Complete seed data documentation
- `SEED_DATA_QUICK_START.md` - Quick reference guide
- `SEED_DATA_CREDENTIALS.md` - Generated credentials (created by seed script)

## API Endpoints

### Authentication
- `POST /api/auth/verify` - Verify Firebase ID token
- `POST /api/auth/refresh` - Refresh session token
- `POST /api/auth/mfa/setup` - Setup MFA
- `POST /api/auth/mfa/verify` - Verify MFA code

### Access Requests
- `POST /api/access/request` - Submit access request
- `GET /api/access/history` - Get user's request history
- `GET /api/access/:id` - Get request details
- `PUT /api/access/:id/resubmit` - Resubmit denied request

### Admin
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/:id` - Update user
- `DELETE /api/admin/users/:id` - Deactivate user
- `GET /api/admin/logs` - Get audit logs
- `POST /api/admin/policy` - Create/update policy
- `GET /api/admin/analytics` - Get system analytics

### Policies
- `GET /api/policy/rules` - Get all active policies
- `POST /api/policy/evaluate` - Evaluate access request (internal)

## Environment Variables

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-here
PORT=5000

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Security
JWT_SECRET_KEY=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_policy_engine.py

# Run with coverage
pytest --cov=app

# Validate seed data
python test_seed_data.py
```

### Code Quality

```bash
# Check syntax
python -m py_compile app/**/*.py

# Format code (if using black)
black app/

# Lint code (if using pylint)
pylint app/
```

## Key Components

### Policy Engine
Evaluates access requests against defined policies using confidence scoring.

**Location:** `app/services/policy_engine.py`

**Key Methods:**
- `evaluate_request()` - Main evaluation orchestrator
- `calculate_confidence_score()` - Computes weighted confidence
- `make_decision()` - Determines grant/deny/escalate

### Intent Analyzer
Analyzes natural language intent descriptions for legitimacy.

**Location:** `app/services/intent_analyzer.py`

**Features:**
- Keyword categorization (academic, legitimate, suspicious)
- Coherence detection
- Contradiction detection
- Scoring (0-100)

### Audit Logger
Comprehensive logging of all security-relevant events.

**Location:** `app/services/audit_logger.py`

**Features:**
- Event logging with severity levels
- Real-time alerts for high-severity events
- 90-day retention policy

### Authentication Service
Handles user authentication, token verification, and MFA.

**Location:** `app/services/auth_service.py`

**Features:**
- Firebase token verification
- JWT session management
- MFA setup and verification
- Failed login tracking

## Security Features

- ✓ JWT-based authentication with HttpOnly cookies
- ✓ CSRF protection on state-changing endpoints
- ✓ Rate limiting (configurable per endpoint)
- ✓ Input sanitization and validation
- ✓ MFA support with TOTP
- ✓ Comprehensive audit logging
- ✓ Role-based access control
- ✓ Encrypted MFA secrets (AES-256)

## Firestore Collections

- `users` - User accounts and profiles
- `policies` - Access control policies
- `accessRequests` - Access request records
- `auditLogs` - System audit logs
- `notifications` - User notifications
- `systemConfig` - System configuration

## Deployment

See `DEPLOYMENT_CHECKLIST.md` for production deployment instructions.

### Quick Deploy (Render)

1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables
4. Deploy

### Quick Deploy (Google Cloud Run)

1. Build Docker image
2. Push to Container Registry
3. Deploy to Cloud Run
4. Configure environment variables

## Troubleshooting

### Firebase Connection Issues

```bash
# Check if credentials file exists
ls firebase-credentials.json

# Validate JSON
python -c "import json; json.load(open('firebase-credentials.json'))"

# Test Firebase connection
python -c "from app.firebase_config import initialize_firebase; initialize_firebase()"
```

### Seed Data Issues

```bash
# Check if seed data exists
python check_seed_data.py

# Re-run seed script (idempotent)
python seed_data.py

# Validate seed data structure
python test_seed_data.py
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
PORT=5001 python run.py
```

## Support

For detailed documentation:
- `SEED_DATA_README.md` - Seed data documentation
- `FIRESTORE_SETUP.md` - Firestore configuration
- `SECURITY_HARDENING.md` - Security best practices
- `../README.md` - Project overview
- `.kiro/specs/zero-trust-security-framework/` - Design specifications

## License

This project is part of an educational security framework implementation.
