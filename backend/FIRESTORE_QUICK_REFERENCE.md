# Firestore Security Rules - Quick Reference

## Task 22 Implementation Summary

✅ **All sub-tasks completed:**
- ✅ Security rules for users collection (users read own, admins read all)
- ✅ Security rules for accessRequests collection (users read own, admins read all)
- ✅ Security rules for auditLogs collection (admin read-only)
- ✅ Security rules for policies collection (admin read/write, others read-only)
- ✅ Composite indexes (userId + timestamp, decision + timestamp)
- ✅ Deployment scripts and documentation

**Requirements Satisfied:** 3.2, 3.3, 3.4, 8.1

---

## Quick Deployment

```bash
cd backend
./deploy-firestore.sh
```

---

## Security Rules Summary

| Collection | User Read | User Write | Admin Read | Admin Write | Backend Write |
|------------|-----------|------------|------------|-------------|---------------|
| users | Own only | ❌ | ✅ All | ✅ | ✅ |
| accessRequests | Own only | ❌ | ✅ All | ❌ | ✅ |
| auditLogs | ❌ | ❌ | ✅ | ❌ | ✅ |
| policies | ✅ All | ❌ | ✅ All | ✅ | ✅ |
| systemConfig | ❌ | ❌ | ✅ | ✅ | ✅ |
| notifications | Own only | Read flag only | ✅ All | ❌ | ✅ |

---

## Indexes Summary

### Access Requests (Most Important)
- `userId + timestamp` ⭐ Most common query
- `decision + timestamp` - Filter by status
- `userId + decision + timestamp` - User's requests by status

### Audit Logs
- `userId + timestamp` - User's activity
- `eventType + timestamp` - Events by type
- `severity + timestamp` - High-priority events
- `result + timestamp` - Failed operations

### Notifications
- `userId + read + timestamp` - Unread notifications

### Policies
- `isActive + priority` - Active policies in order

---

## Testing

### Local Testing
```bash
cd backend
npm install
firebase emulators:start --only firestore  # Terminal 1
npm test                                    # Terminal 2
```

### Manual Testing (Firebase Console)
1. Go to Firestore → Rules → Rules Playground
2. Test user reading own data (should allow)
3. Test user reading other's data (should deny)
4. Test admin reading all data (should allow)

---

## Verification Checklist

After deployment:
- [ ] Rules deployed (check Firebase Console → Firestore → Rules)
- [ ] Indexes enabled (check Firebase Console → Firestore → Indexes)
- [ ] Users can read own data
- [ ] Users cannot read others' data
- [ ] Admins can read all data
- [ ] Backend can write to all collections
- [ ] No "missing index" errors in queries

---

## Common Commands

```bash
# Deploy everything
firebase deploy --only firestore

# Deploy rules only
firebase deploy --only firestore:rules

# Deploy indexes only
firebase deploy --only firestore:indexes

# Validate rules
./deploy-firestore.sh --validate

# View current project
firebase use

# Switch project
firebase use <project-id>
```

---

## Files Created

1. `firestore.rules` - Security rules (already existed, verified)
2. `firestore.indexes.json` - Composite indexes (updated with new indexes)
3. `deploy-firestore.sh` - Automated deployment script
4. `firestore.rules.test.js` - Test suite
5. `package.json` - Test dependencies
6. `FIRESTORE_DEPLOYMENT.md` - Detailed deployment guide
7. `FIRESTORE_SETUP.md` - Complete setup documentation
8. `FIRESTORE_QUICK_REFERENCE.md` - This file

---

## Troubleshooting

**"Missing or insufficient permissions"**
→ Check user's role in Firestore users collection

**"The query requires an index"**
→ Add index to firestore.indexes.json and redeploy

**"Rules deployment failed"**
→ Run: `./deploy-firestore.sh --validate`

**Index stuck building**
→ Wait 5-10 minutes, check Firebase Console

---

## Next Steps

1. Deploy rules and indexes: `./deploy-firestore.sh`
2. Wait 5-10 minutes for indexes to build
3. Verify in Firebase Console
4. Run tests: `npm test`
5. Test in production with real queries

---

## Support Documentation

- **Detailed Guide:** `FIRESTORE_DEPLOYMENT.md`
- **Setup Instructions:** `FIRESTORE_SETUP.md`
- **Test Suite:** `firestore.rules.test.js`
- **Deployment Script:** `deploy-firestore.sh`
