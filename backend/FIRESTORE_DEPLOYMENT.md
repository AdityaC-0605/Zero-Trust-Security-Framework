# Firestore Security Rules and Indexes Deployment Guide

This guide explains how to deploy Firestore security rules and indexes for the Zero Trust Security Framework.

## Prerequisites

1. **Firebase CLI installed**: Install globally using npm
   ```bash
   npm install -g firebase-tools
   ```

2. **Firebase project initialized**: Ensure you have a Firebase project set up
   ```bash
   firebase login
   firebase projects:list
   ```

3. **Project configuration**: Initialize Firebase in the backend directory if not already done
   ```bash
   cd backend
   firebase init firestore
   ```
   - Select your Firebase project
   - Accept default file names (firestore.rules and firestore.indexes.json)

## Security Rules Overview

The `firestore.rules` file implements the following security model:

### Users Collection
- **Read**: Users can read their own data, admins can read all users
- **Write**: Only admins can modify user data
- **Requirements**: 3.2, 3.3, 3.4, 8.1

### Access Requests Collection
- **Read**: Users can read their own requests, admins can read all requests
- **Write**: Only backend service (via Admin SDK) can write
- **Requirements**: 3.2, 3.3, 3.4

### Audit Logs Collection
- **Read**: Admin read-only
- **Write**: Only backend service (via Admin SDK) can write
- **Requirements**: 3.2, 3.3, 3.4

### Policies Collection
- **Read**: All authenticated users can read (to understand access rules)
- **Write**: Only admins can create/update/delete policies
- **Requirements**: 3.2, 3.3, 3.4

### System Configuration
- **Read/Write**: Admin only

### Notifications
- **Read**: Users can read their own notifications
- **Update**: Users can mark their own notifications as read
- **Create/Delete**: Only backend service

## Indexes Overview

The `firestore.indexes.json` file defines composite indexes for efficient queries:

### Audit Logs Indexes
1. `userId + timestamp` - Query logs by user over time
2. `eventType + timestamp` - Query logs by event type
3. `severity + timestamp` - Query logs by severity level
4. `result + timestamp` - Query logs by result (success/failure)

### Access Requests Indexes
1. `userId + timestamp` - Query user's request history (most common)
2. `decision + timestamp` - Query requests by decision status
3. `userId + decision + timestamp` - Query user's requests filtered by decision
4. `requestedResource + timestamp` - Query requests by resource type

### Notifications Indexes
1. `userId + read + timestamp` - Query unread notifications efficiently

### Policies Indexes
1. `isActive + priority` - Query active policies in priority order

## Deployment Steps

### 1. Validate Security Rules

Before deploying, validate the rules syntax:

```bash
cd backend
firebase deploy --only firestore:rules --dry-run
```

### 2. Deploy Security Rules

Deploy the security rules to your Firebase project:

```bash
firebase deploy --only firestore:rules
```

Expected output:
```
✔  Deploy complete!

Project Console: https://console.firebase.google.com/project/YOUR_PROJECT/overview
```

### 3. Deploy Indexes

Deploy the composite indexes:

```bash
firebase deploy --only firestore:indexes
```

**Note**: Index creation can take several minutes to complete. You'll see:
```
✔  firestore: deployed indexes in firestore.indexes.json successfully
```

### 4. Verify Deployment

Check the Firebase Console to verify:

1. **Security Rules**: 
   - Go to Firestore Database → Rules
   - Verify the rules are active and show the correct timestamp

2. **Indexes**:
   - Go to Firestore Database → Indexes
   - Verify all indexes show status "Enabled" (may take 5-10 minutes)

### 5. Test Security Rules

Test the rules using the Firebase Console Rules Playground:

```javascript
// Test 1: User reading own data (should succeed)
auth: { uid: 'user123' }
path: /databases/(default)/documents/users/user123
operation: get

// Test 2: User reading another user's data (should fail)
auth: { uid: 'user123' }
path: /databases/(default)/documents/users/user456
operation: get

// Test 3: Admin reading any user (should succeed)
auth: { uid: 'admin123' }
path: /databases/(default)/documents/users/user456
operation: get
// Note: Requires admin123 to have role='admin' in users collection

// Test 4: User reading own access request (should succeed)
auth: { uid: 'user123' }
path: /databases/(default)/documents/accessRequests/req123
operation: get
// Note: Requires req123 to have userId='user123'

// Test 5: Non-admin reading audit logs (should fail)
auth: { uid: 'user123' }
path: /databases/(default)/documents/auditLogs/log123
operation: get
```

## Deploy Both Rules and Indexes Together

To deploy everything at once:

```bash
cd backend
firebase deploy --only firestore
```

## Rollback (If Needed)

If you need to rollback to a previous version:

1. View deployment history:
   ```bash
   firebase firestore:rules:list
   ```

2. Rollback to a specific version:
   ```bash
   firebase firestore:rules:release <RULESET_ID>
   ```

## Environment-Specific Deployment

### Development Environment
```bash
firebase use development
firebase deploy --only firestore
```

### Production Environment
```bash
firebase use production
firebase deploy --only firestore
```

## Continuous Integration/Deployment

For automated deployments, use a service account:

1. Generate a service account key in Firebase Console
2. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
   ```
3. Deploy in CI/CD pipeline:
   ```bash
   firebase deploy --only firestore --token "$FIREBASE_TOKEN"
   ```

## Monitoring and Maintenance

### Monitor Rule Violations

Check Firebase Console → Firestore → Usage tab for:
- Denied read/write attempts
- Security rule evaluation errors

### Index Performance

Monitor index usage in Firebase Console:
- Firestore Database → Indexes
- Check for "Suggested Indexes" if queries are slow

### Update Rules

When updating rules:
1. Test changes locally using Firebase Emulator
2. Deploy to development environment first
3. Verify functionality
4. Deploy to production

## Troubleshooting

### Issue: "Missing or insufficient permissions"
**Solution**: Verify the user's role in the users collection and ensure authentication token is valid.

### Issue: "The query requires an index"
**Solution**: 
1. Copy the index definition from the error message
2. Add it to `firestore.indexes.json`
3. Deploy: `firebase deploy --only firestore:indexes`

### Issue: "Rules deployment failed"
**Solution**: 
1. Check syntax: `firebase deploy --only firestore:rules --dry-run`
2. Verify helper functions are defined before use
3. Check for circular dependencies in rules

### Issue: "Index creation taking too long"
**Solution**: 
- Large collections may take 30+ minutes to index
- Check status in Firebase Console
- Indexes build in background, app remains functional

## Security Best Practices

1. **Never use wildcards in production**: Always specify exact origins in CORS
2. **Test rules thoroughly**: Use Firebase Emulator for local testing
3. **Principle of least privilege**: Grant minimum necessary permissions
4. **Regular audits**: Review rules quarterly for security gaps
5. **Version control**: Always commit rules and indexes to git
6. **Backup before changes**: Document current rules before modifications

## Additional Resources

- [Firestore Security Rules Documentation](https://firebase.google.com/docs/firestore/security/get-started)
- [Firestore Indexes Documentation](https://firebase.google.com/docs/firestore/query-data/indexing)
- [Firebase CLI Reference](https://firebase.google.com/docs/cli)
- [Security Rules Testing](https://firebase.google.com/docs/rules/unit-tests)

## Verification Checklist

After deployment, verify:

- [ ] Security rules deployed successfully
- [ ] All indexes show "Enabled" status
- [ ] Users can read their own data
- [ ] Users cannot read other users' data (unless admin)
- [ ] Admins can read all collections
- [ ] Non-admins cannot read audit logs
- [ ] Backend service can write to all collections
- [ ] Queries execute without "missing index" errors
- [ ] No security rule violations in console logs

## Support

For issues or questions:
1. Check Firebase Console for error messages
2. Review audit logs for security violations
3. Test rules in Firebase Emulator locally
4. Consult Firebase documentation
