# Seed Data Quick Start Guide

Quick reference for using the seed data script in the Zero Trust Security Framework.

## Quick Commands

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run seed script
python seed_data.py

# Validate seed data (without Firebase)
python test_seed_data.py
```

## Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | student@test.edu | Student123! |
| Faculty | faculty@test.edu | Faculty123! |
| Admin | admin@test.edu | Admin123! |

## Default Policies Summary

| Policy | Resource | Roles | Min Confidence | MFA | Priority |
|--------|----------|-------|----------------|-----|----------|
| Admin Panel | admin_panel | admin | 90 | ✓ | 20 |
| Research Storage | research_storage | faculty, admin | 75 | ✓ | 15 |
| Lab Server | lab_server | faculty, admin | 70 | ✓ | 10 |
| Library Database | library_database | all | 60 | ✗ | 5 |
| Student Portal | student_portal | all | 50 | ✗ | 3 |

## What Gets Created

- ✓ 3 test user accounts (student, faculty, admin)
- ✓ 5 default access policies
- ✓ System configuration with thresholds
- ✓ Keyword categories for intent analysis (68 total keywords)
- ✓ 6 sample access requests
- ✓ Documentation file (SEED_DATA_CREDENTIALS.md)

## Important Notes

⚠️ **Firebase Authentication:** Users are created in Firestore only. You must also create them in Firebase Authentication before they can log in.

⚠️ **Development Only:** These credentials are for development/testing only. Do NOT use in production.

⚠️ **Idempotent:** The script can be run multiple times safely - it checks for existing data.

## Next Steps After Seeding

1. **Create users in Firebase Auth** (via Console or Admin SDK)
2. **Start the backend server:** `python run.py`
3. **Start the frontend:** `cd ../frontend && npm start`
4. **Test login** with any of the test accounts
5. **Submit access requests** to test policy evaluation

## Verification Checklist

After running the seed script, verify in Firebase Console:

- [ ] Firestore has `users` collection with 3 documents
- [ ] Firestore has `policies` collection with 5 documents
- [ ] Firestore has `systemConfig` collection with 2 documents
- [ ] Firestore has `accessRequests` collection with 6 documents
- [ ] Firebase Authentication has 3 test users (must create manually)

## Troubleshooting

**Script fails with "Failed to initialize Firebase"**
- Ensure `firebase-credentials.json` exists in backend directory
- Verify the file is valid JSON
- Check Firebase project configuration

**Users can't log in**
- Users must exist in both Firestore AND Firebase Authentication
- Create them in Firebase Console → Authentication → Users
- Use the same email addresses as in the seed data

**Policies not being applied**
- Check that policies are marked as `isActive: true`
- Verify policy priority (higher priority = evaluated first)
- Check that resource types match exactly

## Clean Up

To remove all seed data:

```bash
# Option 1: Firebase Console
# Go to Firestore Database and delete collections manually

# Option 2: Firebase CLI (use with caution!)
firebase firestore:delete --all-collections
```

## Files Created

- `SEED_DATA_CREDENTIALS.md` - Detailed credentials documentation
- `SEED_DATA_README.md` - Complete usage guide
- `SEED_DATA_QUICK_START.md` - This file

## Support

For detailed information, see:
- `SEED_DATA_README.md` - Full documentation
- `../README.md` - Project documentation
- `.kiro/specs/zero-trust-security-framework/design.md` - System design

## Requirements Implemented

- ✓ Requirement 5.1: Policy-based evaluation
- ✓ Requirement 11.2: Policy configuration
