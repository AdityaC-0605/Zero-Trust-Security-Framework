# Seed Data Script

This script populates the Zero Trust Security Framework database with default policies, test users, system configuration, keyword categories, and sample access requests for development and testing purposes.

## Requirements

- Python 3.8+
- Firebase Admin SDK configured
- Valid Firebase credentials file (`firebase-credentials.json`)
- All dependencies from `requirements.txt` installed

## What Gets Created

### 1. Test User Accounts

Three test user accounts are created, one for each role:

- **Student Account**
  - Email: `student@test.edu`
  - Password: `Student123!`
  - Role: student
  - Department: Computer Science

- **Faculty Account**
  - Email: `faculty@test.edu`
  - Password: `Faculty123!`
  - Role: faculty
  - Department: Computer Science

- **Admin Account**
  - Email: `admin@test.edu`
  - Password: `Admin123!`
  - Role: admin
  - Department: IT Administration

**Note:** These users are created in Firestore only. You must also create them in Firebase Authentication manually or through the Firebase Console before they can log in.

### 2. Default Policies

Five default access policies are created:

1. **Lab Server Access** (Priority: 10)
   - For laboratory servers
   - Allowed: faculty, admin
   - Min Confidence: 70
   - MFA Required: Yes
   - Time: 6 AM - 10 PM, Weekdays only

2. **Library Database Access** (Priority: 5)
   - For library databases
   - Allowed: student, faculty, admin
   - Min Confidence: 60
   - MFA Required: No

3. **Admin Panel Access** (Priority: 20)
   - For administrative panel
   - Allowed: admin only
   - Min Confidence: 90
   - MFA Required: Yes

4. **Student Portal Access** (Priority: 3)
   - For student information portal
   - Allowed: student, faculty, admin
   - Min Confidence: 50
   - MFA Required: No

5. **Research Data Storage** (Priority: 15)
   - For research data storage
   - Allowed: faculty, admin
   - Min Confidence: 75
   - MFA Required: Yes

### 3. System Configuration

Creates a system configuration document with:

- Session timeout: 60 minutes
- Max login attempts: 5
- Lockout duration: 30 minutes
- Log retention: 90 days
- Confidence thresholds (auto-approve: 90, require MFA: 50-89, deny: <50)
- Email notification settings
- Rate limits
- Security settings

### 4. Keyword Categories

Populates keyword categories used by the intent analyzer:

- **Academic keywords** (25 keywords): research, study, assignment, project, etc.
- **Legitimate keywords** (15 keywords): work, official, authorized, required, etc.
- **Suspicious keywords** (16 keywords): urgent, emergency, testing, temporary, etc.
- **Administrative keywords** (12 keywords): configuration, setup, maintenance, etc.

### 5. Sample Access Requests

Creates 6 sample access requests demonstrating different scenarios:

- Legitimate academic requests (expected: granted)
- Role-appropriate requests (expected: granted with MFA)
- Inappropriate requests (expected: denied)
- Various resource types and urgency levels

## Usage

### Prerequisites

1. Ensure Firebase is configured:
   ```bash
   # Make sure firebase-credentials.json exists
   ls firebase-credentials.json
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Script

From the `backend` directory:

```bash
python seed_data.py
```

### Expected Output

```
============================================================
Zero Trust Security Framework - Seed Data Script
============================================================

Initializing Firebase...
✓ Firebase initialized successfully

=== Creating Test Users ===
✓ Created user 'student' (student@test.edu)
  User ID: test_student_user_abc12345
  Password: Student123!
✓ Created user 'faculty' (faculty@test.edu)
  User ID: test_faculty_user_def67890
  Password: Faculty123!
✓ Created user 'admin' (admin@test.edu)
  User ID: test_admin_user_ghi24680
  Password: Admin123!

=== Creating Default Policies ===
✓ Created policy 'Lab Server Access' (Priority: 10)
✓ Created policy 'Library Database Access' (Priority: 5)
✓ Created policy 'Admin Panel Access' (Priority: 20)
✓ Created policy 'Student Portal Access' (Priority: 3)
✓ Created policy 'Research Data Storage' (Priority: 15)

=== Creating System Configuration ===
✓ Created system configuration
  Session Timeout: 60 minutes
  Max Login Attempts: 5
  Confidence Thresholds: Auto-approve >= 90

=== Populating Keyword Categories ===
✓ Created keyword categories
  academic: 25 keywords
  legitimate: 15 keywords
  suspicious: 16 keywords
  administrative: 12 keywords

=== Creating Sample Access Requests ===
✓ Created sample request: student → library_database
  Expected: granted
✓ Created sample request: faculty → lab_server
  Expected: granted_with_mfa
✓ Created sample request: student → admin_panel
  Expected: denied
✓ Created sample request: admin → admin_panel
  Expected: granted_with_mfa
✓ Created sample request: student → student_portal
  Expected: granted
✓ Created sample request: faculty → research_storage
  Expected: granted_with_mfa

✓ Credentials documented in SEED_DATA_CREDENTIALS.md

============================================================
Seed Data Population Complete
============================================================
✓ Test Users Created: 3
✓ Default Policies Created: 5
✓ Sample Requests Created: 6
✓ System Configuration: Created
✓ Keyword Categories: Populated

You can now use the test accounts to log in and test the system.
See SEED_DATA_CREDENTIALS.md for detailed credentials and configuration.
============================================================
```

## Post-Seeding Steps

### 1. Create Users in Firebase Authentication

The seed script creates user documents in Firestore, but you must also create the users in Firebase Authentication:

**Option A: Using Firebase Console**
1. Go to Firebase Console → Authentication → Users
2. Click "Add user"
3. Enter email and password for each test user
4. The UID should match the user_id in Firestore (or update Firestore with the Firebase UID)

**Option B: Using Firebase Admin SDK**
```python
from firebase_admin import auth

# Create users in Firebase Auth
auth.create_user(
    email='student@test.edu',
    password='Student123!',
    uid='test_student_user_abc12345'  # Use the ID from seed script
)
```

### 2. Verify Data in Firestore

Check that all collections were created:
- `users` - Should have 3 documents
- `policies` - Should have 5 documents
- `systemConfig` - Should have 2 documents (settings, keywordCategories)
- `accessRequests` - Should have 6 documents

### 3. Test the System

1. Start the backend server:
   ```bash
   python run.py
   ```

2. Start the frontend:
   ```bash
   cd ../frontend
   npm start
   ```

3. Log in with test credentials and verify:
   - Authentication works
   - Role-based access control works
   - Access request submission works
   - Policy evaluation works

## Re-running the Script

The script is idempotent - it checks if data already exists before creating it:

- If users already exist (by email), they are skipped
- If policies already exist (by name), they are skipped
- If system config exists, it is skipped
- If keyword categories exist, they are skipped

You can safely re-run the script without duplicating data.

## Cleaning Up Seed Data

To remove all seed data:

1. **Delete from Firestore:**
   - Go to Firebase Console → Firestore Database
   - Delete the collections: `users`, `policies`, `systemConfig`, `accessRequests`

2. **Delete from Firebase Authentication:**
   - Go to Firebase Console → Authentication → Users
   - Delete the test user accounts

3. **Or use Firebase CLI:**
   ```bash
   # Delete all data (use with caution!)
   firebase firestore:delete --all-collections
   ```

## Troubleshooting

### Error: "Failed to initialize Firebase"

**Solution:** Ensure `firebase-credentials.json` exists and is valid:
```bash
# Check if file exists
ls firebase-credentials.json

# Verify it's valid JSON
python -c "import json; json.load(open('firebase-credentials.json'))"
```

### Error: "Policy with name 'X' already exists"

**Solution:** This is normal if you're re-running the script. The script will skip existing policies.

### Error: "User already exists"

**Solution:** This is normal if you're re-running the script. The script will skip existing users.

### Users can't log in

**Solution:** Make sure users are created in Firebase Authentication, not just Firestore:
1. Go to Firebase Console → Authentication
2. Verify the test users exist
3. If not, create them manually or use the Firebase Admin SDK

## Security Notes

⚠️ **IMPORTANT:** These credentials are for **DEVELOPMENT ONLY**

- Do NOT use these credentials in production
- Do NOT commit `firebase-credentials.json` to version control
- Change all passwords before deploying to production
- Use environment-specific configurations
- Implement proper secret management for production

## Related Files

- `seed_data.py` - Main seed script
- `SEED_DATA_CREDENTIALS.md` - Generated credentials documentation
- `firebase-credentials.json` - Firebase service account credentials (not in repo)
- `.env` - Environment variables configuration

## Requirements Reference

This seed script implements:
- **Requirement 5.1:** Policy-based evaluation with default policies
- **Requirement 11.2:** Policy configuration with resource types and rules

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Firebase setup documentation
3. Check the main project README
4. Review the design document for data model specifications
