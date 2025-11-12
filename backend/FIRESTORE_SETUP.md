# Firestore Security Rules and Indexes Setup

This document provides a complete guide for setting up, testing, and deploying Firestore security rules and indexes for the Zero Trust Security Framework.

## Overview

The Firestore security implementation ensures:
- **Role-based access control** (Requirements 3.2, 3.3, 3.4)
- **Data isolation** between users
- **Admin-only access** to sensitive collections
- **Backend service control** over write operations
- **Optimized query performance** through composite indexes

## Files

- `firestore.rules` - Security rules defining access control
- `firestore.indexes.json` - Composite indexes for query optimization
- `deploy-firestore.sh` - Automated deployment script
- `firestore.rules.test.js` - Security rules test suite
- `package.json` - Test dependencies
- `FIRESTORE_DEPLOYMENT.md` - Detailed deployment guide

## Quick Start

### 1. Prerequisites

Install Firebase CLI:
```bash
npm install -g firebase-tools
```

Login to Firebase:
```bash
firebase login
```

### 2. Initialize Firebase (First Time Only)

```bash
cd backend
firebase init firestore
```

Select your Firebase project and accept default file names.

### 3. Deploy Rules and Indexes

Using the deployment script (recommended):
```bash
cd backend
./deploy-firestore.sh
```

Or manually:
```bash
firebase deploy --only firestore
```

### 4. Verify Deployment

Check Firebase Console:
- Rules: https://console.firebase.google.com/project/YOUR_PROJECT/firestore/rules
- Indexes: https://console.firebase.google.com/project/YOUR_PROJECT/firestore/indexes

## Security Rules Details

### Users Collection (`users/{userId}`)

**Access Control:**
- **Read**: Users can read their own document, admins can read all
- **Write**: Only admins can create/update/delete users

**Use Cases:**
- User profile viewing
- Admin user management
- Role verification

**Requirements:** 3.2, 3.3, 3.4, 8.1

### Access Requests Collection (`accessRequests/{requestId}`)

**Access Control:**
- **Read**: Users can read their own requests, admins can read all
- **Write**: Only backend service (via Admin SDK)

**Use Cases:**
- User viewing request history
- Admin reviewing all requests
- Backend creating/updating requests

**Requirements:** 3.2, 3.3, 3.4

### Audit Logs Collection (`auditLogs/{logId}`)

**Access Control:**
- **Read**: Admin only
- **Write**: Only backend service (via Admin SDK)

**Use Cases:**
- Admin viewing system audit trail
- Backend logging security events
- Compliance reporting

**Requirements:** 3.2, 3.3, 3.4

### Policies Collection (`policies/{policyId}`)

**Access Control:**
- **Read**: All authenticated users (to understand access rules)
- **Write**: Admin only

**Use Cases:**
- Users viewing applicable policies
- Admin configuring access rules
- Policy engine evaluating requests

**Requirements:** 3.2, 3.3, 3.4

### Notifications Collection (`notifications/{notificationId}`)

**Access Control:**
- **Read**: Users can read their own notifications
- **Update**: Users can mark their own notifications as read (read field only)
- **Create/Delete**: Only backend service

**Use Cases:**
- User viewing notifications
- User marking notifications as read
- Backend sending notifications

### System Configuration (`systemConfig/{document}`)

**Access Control:**
- **Read/Write**: Admin only

**Use Cases:**
- Admin configuring system settings
- Backend reading configuration

## Indexes Details

### Why Indexes Are Needed

Firestore requires composite indexes for queries that:
1. Use multiple fields in ordering
2. Combine equality filters with ordering
3. Use inequality filters on multiple fields

### Defined Indexes

#### Audit Logs Indexes

1. **userId + timestamp (DESC)**
   - Query: Get user's audit history
   - Example: `auditLogs.where('userId', '==', uid).orderBy('timestamp', 'desc')`

2. **eventType + timestamp (DESC)**
   - Query: Get events by type
   - Example: `auditLogs.where('eventType', '==', 'authentication').orderBy('timestamp', 'desc')`

3. **severity + timestamp (DESC)**
   - Query: Get high-severity events
   - Example: `auditLogs.where('severity', '==', 'critical').orderBy('timestamp', 'desc')`

4. **result + timestamp (DESC)**
   - Query: Get failed operations
   - Example: `auditLogs.where('result', '==', 'failure').orderBy('timestamp', 'desc')`

#### Access Requests Indexes

1. **userId + timestamp (DESC)**
   - Query: Get user's request history
   - Example: `accessRequests.where('userId', '==', uid).orderBy('timestamp', 'desc')`
   - **Most common query**

2. **decision + timestamp (DESC)**
   - Query: Get requests by decision status
   - Example: `accessRequests.where('decision', '==', 'denied').orderBy('timestamp', 'desc')`

3. **userId + decision + timestamp (DESC)**
   - Query: Get user's requests filtered by decision
   - Example: `accessRequests.where('userId', '==', uid).where('decision', '==', 'granted').orderBy('timestamp', 'desc')`

#### Notifications Indexes

1. **userId + read + timestamp (DESC)**
   - Query: Get unread notifications
   - Example: `notifications.where('userId', '==', uid).where('read', '==', false).orderBy('timestamp', 'desc')`

#### Policies Indexes

1. **isActive + priority (DESC)**
   - Query: Get active policies in priority order
   - Example: `policies.where('isActive', '==', true).orderBy('priority', 'desc')`

## Testing Security Rules

### Local Testing with Firebase Emulator

1. **Install test dependencies:**
   ```bash
   cd backend
   npm install
   ```

2. **Start Firebase Emulator:**
   ```bash
   firebase emulators:start --only firestore
   ```

3. **Run tests (in another terminal):**
   ```bash
   cd backend
   npm test
   ```

### Manual Testing in Firebase Console

1. Go to Firestore → Rules → Rules Playground
2. Test scenarios:

**Test 1: User reading own data**
```javascript
// Should ALLOW
auth: { uid: 'user123' }
path: /databases/(default)/documents/users/user123
operation: get
```

**Test 2: User reading another user's data**
```javascript
// Should DENY
auth: { uid: 'user123' }
path: /databases/(default)/documents/users/user456
operation: get
```

**Test 3: Admin reading any user**
```javascript
// Should ALLOW (if user123 has role='admin')
auth: { uid: 'user123' }
path: /databases/(default)/documents/users/user456
operation: get
```

## Deployment Scenarios

### Development Environment

```bash
firebase use development
./deploy-firestore.sh
```

### Staging Environment

```bash
firebase use staging
./deploy-firestore.sh
```

### Production Environment

```bash
firebase use production
./deploy-firestore.sh
```

### CI/CD Pipeline

```bash
# In your CI/CD configuration
firebase deploy --only firestore --token "$FIREBASE_TOKEN"
```

## Monitoring and Maintenance

### Check for Rule Violations

1. Go to Firebase Console → Firestore → Usage
2. Look for "Permission denied" errors
3. Review patterns and adjust rules if needed

### Monitor Index Performance

1. Go to Firebase Console → Firestore → Indexes
2. Check for "Suggested Indexes" warnings
3. Add suggested indexes to `firestore.indexes.json`

### Update Rules

When updating rules:
1. Test locally with emulator first
2. Deploy to development environment
3. Verify functionality
4. Deploy to production

## Troubleshooting

### "Missing or insufficient permissions"

**Cause:** User doesn't have required role or trying to access unauthorized data

**Solution:**
1. Verify user's role in Firestore users collection
2. Check authentication token is valid
3. Review security rules for the collection

### "The query requires an index"

**Cause:** Query uses fields not covered by existing indexes

**Solution:**
1. Copy the index definition from error message
2. Add to `firestore.indexes.json`
3. Deploy: `firebase deploy --only firestore:indexes`
4. Wait 5-10 minutes for index to build

### "Rules deployment failed"

**Cause:** Syntax error in security rules

**Solution:**
1. Validate syntax: `./deploy-firestore.sh --validate`
2. Check for typos in helper functions
3. Ensure all functions are defined before use

### Index creation stuck

**Cause:** Large collection or Firebase service issue

**Solution:**
1. Check Firebase Status page
2. Wait up to 30 minutes for large collections
3. Contact Firebase support if stuck > 1 hour

## Security Best Practices

1. **Never disable security rules** in production
2. **Test rules thoroughly** before deploying
3. **Use least privilege principle** - grant minimum necessary access
4. **Regular audits** - review rules quarterly
5. **Monitor violations** - set up alerts for denied access attempts
6. **Version control** - always commit rules to git
7. **Document changes** - explain why rules were modified

## Performance Optimization

### Index Strategy

1. **Create indexes for common queries** - analyze query patterns
2. **Avoid over-indexing** - each index has storage cost
3. **Monitor index usage** - remove unused indexes
4. **Composite indexes** - prefer over multiple single-field indexes

### Query Optimization

1. **Use indexed fields** - ensure queries use indexed fields
2. **Limit results** - use `.limit()` to reduce data transfer
3. **Pagination** - implement cursor-based pagination
4. **Cache results** - cache frequently accessed data client-side

## Compliance and Auditing

### Data Access Logging

All data access is logged through:
1. Firestore audit logs (admin access)
2. Backend audit logger (all operations)
3. Firebase Console activity logs

### Compliance Requirements

The security rules support:
- **FERPA** - Student data isolation
- **GDPR** - User data access control
- **SOC 2** - Audit trail and access controls

### Regular Reviews

Schedule quarterly reviews of:
1. Security rules effectiveness
2. Access patterns and violations
3. Index performance
4. User role assignments

## Additional Resources

- [Firestore Security Rules Documentation](https://firebase.google.com/docs/firestore/security/get-started)
- [Firestore Indexes Guide](https://firebase.google.com/docs/firestore/query-data/indexing)
- [Firebase CLI Reference](https://firebase.google.com/docs/cli)
- [Rules Unit Testing](https://firebase.google.com/docs/rules/unit-tests)
- [Best Practices](https://firebase.google.com/docs/firestore/security/rules-conditions)

## Support

For issues:
1. Check Firebase Console for error messages
2. Review audit logs for security violations
3. Test rules locally with emulator
4. Consult Firebase documentation
5. Contact Firebase support

## Verification Checklist

After deployment, verify:

- [ ] Security rules deployed successfully
- [ ] All indexes show "Enabled" status (wait 5-10 minutes)
- [ ] Users can read their own data
- [ ] Users cannot read other users' data (unless admin)
- [ ] Admins can read all collections
- [ ] Non-admins cannot read audit logs
- [ ] Backend service can write to all collections
- [ ] Queries execute without "missing index" errors
- [ ] No security rule violations in console logs
- [ ] Test suite passes all tests
- [ ] Rules Playground tests pass
- [ ] Production queries perform well

## Summary

The Firestore security implementation provides:
- ✅ Role-based access control (Requirements 3.2, 3.3, 3.4, 8.1)
- ✅ Data isolation between users
- ✅ Admin-only access to sensitive data
- ✅ Backend service control over writes
- ✅ Optimized query performance
- ✅ Comprehensive audit trail
- ✅ Compliance-ready security model

Deploy with confidence using the provided tools and documentation!
