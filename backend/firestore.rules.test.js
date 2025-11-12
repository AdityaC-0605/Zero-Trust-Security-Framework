/**
 * Firestore Security Rules Test Suite
 * 
 * Run these tests using Firebase Emulator:
 * 1. Install: npm install -g @firebase/rules-unit-testing
 * 2. Start emulator: firebase emulators:start --only firestore
 * 3. Run tests: npm test (or node firestore.rules.test.js)
 * 
 * Requirements tested: 3.2, 3.3, 3.4, 8.1
 */

const { initializeTestEnvironment, assertSucceeds, assertFails } = require('@firebase/rules-unit-testing');
const fs = require('fs');

let testEnv;

// Test data
const STUDENT_UID = 'student123';
const FACULTY_UID = 'faculty456';
const ADMIN_UID = 'admin789';
const OTHER_USER_UID = 'other999';

// Setup test environment
async function setupTestEnvironment() {
  testEnv = await initializeTestEnvironment({
    projectId: 'zero-trust-test',
    firestore: {
      rules: fs.readFileSync('firestore.rules', 'utf8'),
      host: 'localhost',
      port: 8080
    }
  });
}

// Cleanup after tests
async function cleanup() {
  await testEnv.cleanup();
}

// Helper to create authenticated context
function getAuthContext(uid, role = 'student') {
  return testEnv.authenticatedContext(uid);
}

// Helper to create unauthenticated context
function getUnauthContext() {
  return testEnv.unauthenticatedContext();
}

// Helper to seed test data
async function seedTestData() {
  const adminDb = testEnv.withSecurityRulesDisabled(context => context.firestore());
  
  // Create test users
  await adminDb.collection('users').doc(STUDENT_UID).set({
    userId: STUDENT_UID,
    email: 'student@example.com',
    role: 'student',
    name: 'Test Student',
    isActive: true
  });
  
  await adminDb.collection('users').doc(FACULTY_UID).set({
    userId: FACULTY_UID,
    email: 'faculty@example.com',
    role: 'faculty',
    name: 'Test Faculty',
    isActive: true
  });
  
  await adminDb.collection('users').doc(ADMIN_UID).set({
    userId: ADMIN_UID,
    email: 'admin@example.com',
    role: 'admin',
    name: 'Test Admin',
    isActive: true
  });
  
  await adminDb.collection('users').doc(OTHER_USER_UID).set({
    userId: OTHER_USER_UID,
    email: 'other@example.com',
    role: 'student',
    name: 'Other Student',
    isActive: true
  });
  
  // Create test access requests
  await adminDb.collection('accessRequests').doc('req_student').set({
    requestId: 'req_student',
    userId: STUDENT_UID,
    resource: 'lab_server',
    intent: 'Need access for research project',
    decision: 'granted',
    timestamp: new Date()
  });
  
  await adminDb.collection('accessRequests').doc('req_faculty').set({
    requestId: 'req_faculty',
    userId: FACULTY_UID,
    resource: 'admin_panel',
    intent: 'Need to configure settings',
    decision: 'denied',
    timestamp: new Date()
  });
  
  // Create test audit logs
  await adminDb.collection('auditLogs').doc('log1').set({
    logId: 'log1',
    eventType: 'authentication',
    userId: STUDENT_UID,
    action: 'login',
    result: 'success',
    timestamp: new Date(),
    severity: 'low'
  });
  
  // Create test policies
  await adminDb.collection('policies').doc('policy1').set({
    policyId: 'policy1',
    name: 'Lab Server Access',
    resourceType: 'lab_server',
    allowedRoles: ['faculty', 'admin'],
    minConfidence: 70,
    isActive: true,
    priority: 1
  });
  
  // Create test notifications
  await adminDb.collection('notifications').doc('notif_student').set({
    notificationId: 'notif_student',
    userId: STUDENT_UID,
    type: 'access_decision',
    title: 'Access Request Approved',
    message: 'Your request has been approved',
    read: false,
    timestamp: new Date()
  });
}

// Test Suite: Users Collection
async function testUsersCollection() {
  console.log('\n📋 Testing Users Collection...');
  
  // Test 1: User can read own data
  const studentDb = getAuthContext(STUDENT_UID).firestore();
  await assertSucceeds(
    studentDb.collection('users').doc(STUDENT_UID).get()
  );
  console.log('  ✓ User can read own data');
  
  // Test 2: User cannot read other user's data
  await assertFails(
    studentDb.collection('users').doc(OTHER_USER_UID).get()
  );
  console.log('  ✓ User cannot read other user\'s data');
  
  // Test 3: Admin can read any user's data
  const adminDb = getAuthContext(ADMIN_UID).firestore();
  await assertSucceeds(
    adminDb.collection('users').doc(STUDENT_UID).get()
  );
  console.log('  ✓ Admin can read any user\'s data');
  
  // Test 4: User cannot write to users collection
  await assertFails(
    studentDb.collection('users').doc(STUDENT_UID).update({ name: 'Hacked' })
  );
  console.log('  ✓ User cannot write to users collection');
  
  // Test 5: Admin can write to users collection
  await assertSucceeds(
    adminDb.collection('users').doc(STUDENT_UID).update({ name: 'Updated Name' })
  );
  console.log('  ✓ Admin can write to users collection');
  
  // Test 6: Unauthenticated user cannot read
  const unauthDb = getUnauthContext().firestore();
  await assertFails(
    unauthDb.collection('users').doc(STUDENT_UID).get()
  );
  console.log('  ✓ Unauthenticated user cannot read users');
}

// Test Suite: Access Requests Collection
async function testAccessRequestsCollection() {
  console.log('\n📋 Testing Access Requests Collection...');
  
  // Test 1: User can read own access requests
  const studentDb = getAuthContext(STUDENT_UID).firestore();
  await assertSucceeds(
    studentDb.collection('accessRequests').doc('req_student').get()
  );
  console.log('  ✓ User can read own access requests');
  
  // Test 2: User cannot read other user's access requests
  await assertFails(
    studentDb.collection('accessRequests').doc('req_faculty').get()
  );
  console.log('  ✓ User cannot read other user\'s access requests');
  
  // Test 3: Admin can read any access request
  const adminDb = getAuthContext(ADMIN_UID).firestore();
  await assertSucceeds(
    adminDb.collection('accessRequests').doc('req_student').get()
  );
  await assertSucceeds(
    adminDb.collection('accessRequests').doc('req_faculty').get()
  );
  console.log('  ✓ Admin can read any access request');
  
  // Test 4: User cannot write to access requests (backend only)
  await assertFails(
    studentDb.collection('accessRequests').doc('new_req').set({
      userId: STUDENT_UID,
      resource: 'test'
    })
  );
  console.log('  ✓ User cannot write to access requests');
  
  // Test 5: Admin cannot write to access requests (backend only)
  await assertFails(
    adminDb.collection('accessRequests').doc('new_req').set({
      userId: STUDENT_UID,
      resource: 'test'
    })
  );
  console.log('  ✓ Admin cannot write to access requests (backend only)');
}

// Test Suite: Audit Logs Collection
async function testAuditLogsCollection() {
  console.log('\n📋 Testing Audit Logs Collection...');
  
  // Test 1: Regular user cannot read audit logs
  const studentDb = getAuthContext(STUDENT_UID).firestore();
  await assertFails(
    studentDb.collection('auditLogs').doc('log1').get()
  );
  console.log('  ✓ Regular user cannot read audit logs');
  
  // Test 2: Admin can read audit logs
  const adminDb = getAuthContext(ADMIN_UID).firestore();
  await assertSucceeds(
    adminDb.collection('auditLogs').doc('log1').get()
  );
  console.log('  ✓ Admin can read audit logs');
  
  // Test 3: No one can write to audit logs (backend only)
  await assertFails(
    adminDb.collection('auditLogs').doc('new_log').set({
      eventType: 'test'
    })
  );
  console.log('  ✓ No one can write to audit logs (backend only)');
  
  // Test 4: User cannot write to audit logs
  await assertFails(
    studentDb.collection('auditLogs').doc('new_log').set({
      eventType: 'test'
    })
  );
  console.log('  ✓ User cannot write to audit logs');
}

// Test Suite: Policies Collection
async function testPoliciesCollection() {
  console.log('\n📋 Testing Policies Collection...');
  
  // Test 1: Authenticated user can read policies
  const studentDb = getAuthContext(STUDENT_UID).firestore();
  await assertSucceeds(
    studentDb.collection('policies').doc('policy1').get()
  );
  console.log('  ✓ Authenticated user can read policies');
  
  // Test 2: User cannot write to policies
  await assertFails(
    studentDb.collection('policies').doc('policy1').update({
      minConfidence: 50
    })
  );
  console.log('  ✓ User cannot write to policies');
  
  // Test 3: Admin can read policies
  const adminDb = getAuthContext(ADMIN_UID).firestore();
  await assertSucceeds(
    adminDb.collection('policies').doc('policy1').get()
  );
  console.log('  ✓ Admin can read policies');
  
  // Test 4: Admin can write to policies
  await assertSucceeds(
    adminDb.collection('policies').doc('policy1').update({
      minConfidence: 80
    })
  );
  console.log('  ✓ Admin can write to policies');
  
  // Test 5: Unauthenticated user cannot read policies
  const unauthDb = getUnauthContext().firestore();
  await assertFails(
    unauthDb.collection('policies').doc('policy1').get()
  );
  console.log('  ✓ Unauthenticated user cannot read policies');
}

// Test Suite: Notifications Collection
async function testNotificationsCollection() {
  console.log('\n📋 Testing Notifications Collection...');
  
  // Test 1: User can read own notifications
  const studentDb = getAuthContext(STUDENT_UID).firestore();
  await assertSucceeds(
    studentDb.collection('notifications').doc('notif_student').get()
  );
  console.log('  ✓ User can read own notifications');
  
  // Test 2: User can mark own notification as read
  await assertSucceeds(
    studentDb.collection('notifications').doc('notif_student').update({
      read: true
    })
  );
  console.log('  ✓ User can mark own notification as read');
  
  // Test 3: User cannot modify other fields
  await assertFails(
    studentDb.collection('notifications').doc('notif_student').update({
      message: 'Hacked message'
    })
  );
  console.log('  ✓ User cannot modify other notification fields');
  
  // Test 4: User cannot create notifications (backend only)
  await assertFails(
    studentDb.collection('notifications').doc('new_notif').set({
      userId: STUDENT_UID,
      message: 'Test'
    })
  );
  console.log('  ✓ User cannot create notifications (backend only)');
  
  // Test 5: User cannot delete notifications (backend only)
  await assertFails(
    studentDb.collection('notifications').doc('notif_student').delete()
  );
  console.log('  ✓ User cannot delete notifications (backend only)');
}

// Test Suite: System Configuration
async function testSystemConfigCollection() {
  console.log('\n📋 Testing System Configuration...');
  
  // Test 1: Regular user cannot read system config
  const studentDb = getAuthContext(STUDENT_UID).firestore();
  await assertFails(
    studentDb.collection('systemConfig').doc('settings').get()
  );
  console.log('  ✓ Regular user cannot read system config');
  
  // Test 2: Admin can read system config
  const adminDb = getAuthContext(ADMIN_UID).firestore();
  
  // First seed the config
  const adminContext = testEnv.withSecurityRulesDisabled(context => context.firestore());
  await adminContext.collection('systemConfig').doc('settings').set({
    mfaRequired: false,
    sessionTimeout: 60
  });
  
  await assertSucceeds(
    adminDb.collection('systemConfig').doc('settings').get()
  );
  console.log('  ✓ Admin can read system config');
  
  // Test 3: Admin can write system config
  await assertSucceeds(
    adminDb.collection('systemConfig').doc('settings').update({
      sessionTimeout: 30
    })
  );
  console.log('  ✓ Admin can write system config');
}

// Main test runner
async function runTests() {
  console.log('🚀 Starting Firestore Security Rules Tests');
  console.log('==========================================\n');
  
  try {
    await setupTestEnvironment();
    console.log('✓ Test environment initialized');
    
    await seedTestData();
    console.log('✓ Test data seeded\n');
    
    await testUsersCollection();
    await testAccessRequestsCollection();
    await testAuditLogsCollection();
    await testPoliciesCollection();
    await testNotificationsCollection();
    await testSystemConfigCollection();
    
    console.log('\n==========================================');
    console.log('✅ All tests passed!');
    console.log('==========================================\n');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    process.exit(1);
  } finally {
    await cleanup();
  }
}

// Run tests if executed directly
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { runTests };
