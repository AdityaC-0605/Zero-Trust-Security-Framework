# Deploy Firestore Indexes

## Issue
The application is showing errors like:
```
Error fetching notifications: 400 The query requires an index. You can create it here: https://console.firebase.google.com/...
```

This happens because Firestore requires composite indexes for queries that filter on multiple fields or order by fields.

## Solution: Deploy Indexes

### Option 1: Automatic Deployment (Recommended)

The indexes are already defined in `firestore.indexes.json`. Deploy them using:

```bash
cd backend
chmod +x deploy-indexes.sh
./deploy-indexes.sh
```

**Prerequisites:**
- Firebase CLI installed: `npm install -g firebase-tools`
- Logged in to Firebase: `firebase login`
- Project selected: `firebase use zero-trust-security-framework` (or set in `backend/.firebaserc`)

**Note:** The script will automatically run from the `backend/` directory where `firebase.json` is located.

### Option 2: Manual Deployment via Firebase Console

1. Click on any of the error links in the terminal output
2. Firebase Console will open with the index creation form pre-filled
3. Click "Create Index"
4. Wait for the index to build (can take a few minutes)

### Option 3: Deploy via Firebase CLI

```bash
cd backend
firebase deploy --only firestore:indexes
```

## Required Indexes

The following indexes are already defined in `firestore.indexes.json`:

1. **notifications** collection:
   - `userId` (ASC) + `timestamp` (DESC)
   - `userId` (ASC) + `read` (ASC) + `timestamp` (DESC)

2. **accessRequests** collection:
   - `userId` (ASC) + `timestamp` (DESC)

3. **auditLogs** collection:
   - Multiple indexes for filtering by userId, eventType, severity, result with timestamp ordering

## Verify Index Status

Check index status at:
https://console.firebase.google.com/project/zero-trust-security-framework/firestore/indexes

Indexes show as "Building" initially, then "Enabled" when ready.

## Note

The application will continue to work even with missing indexes, but:
- Queries may be slower
- Some queries may fail with 400 errors
- You'll see warnings in the logs

Once indexes are deployed and built, these warnings will disappear.
