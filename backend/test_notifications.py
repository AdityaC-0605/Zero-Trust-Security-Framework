"""
Test Notification Functionality
Tests for notification creation, retrieval, and management
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from app.firebase_config import get_firestore_client
from app.models.notification import (
    Notification,
    create_notification,
    get_notification_by_id,
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_count,
    delete_expired_notifications
)


def test_notification_creation():
    """Test creating a notification"""
    print("\n=== Testing Notification Creation ===")
    
    try:
        db = get_firestore_client()
        
        # Create a test notification
        notification = create_notification(
            db=db,
            user_id="test_user_123",
            notification_type="access_decision",
            title="Test Notification",
            message="This is a test notification",
            related_resource_id="request_123"
        )
        
        print(f"✓ Notification created successfully")
        print(f"  - ID: {notification.notification_id}")
        print(f"  - User ID: {notification.user_id}")
        print(f"  - Type: {notification.type}")
        print(f"  - Title: {notification.title}")
        print(f"  - Message: {notification.message}")
        print(f"  - Read: {notification.read}")
        
        return notification.notification_id
    except Exception as e:
        print(f"✗ Error creating notification: {str(e)}")
        return None


def test_notification_retrieval(notification_id):
    """Test retrieving a notification by ID"""
    print("\n=== Testing Notification Retrieval ===")
    
    try:
        db = get_firestore_client()
        
        # Get notification by ID
        notification = get_notification_by_id(db, notification_id)
        
        if notification:
            print(f"✓ Notification retrieved successfully")
            print(f"  - ID: {notification.notification_id}")
            print(f"  - Title: {notification.title}")
            print(f"  - Read: {notification.read}")
            return True
        else:
            print(f"✗ Notification not found")
            return False
    except Exception as e:
        print(f"✗ Error retrieving notification: {str(e)}")
        return False


def test_user_notifications():
    """Test retrieving all notifications for a user"""
    print("\n=== Testing User Notifications Retrieval ===")
    
    try:
        db = get_firestore_client()
        
        # Get all notifications for test user
        notifications = get_user_notifications(db, "test_user_123", unread_only=False)
        
        print(f"✓ Retrieved {len(notifications)} notifications for user")
        
        # Get only unread notifications
        unread_notifications = get_user_notifications(db, "test_user_123", unread_only=True)
        print(f"✓ Retrieved {len(unread_notifications)} unread notifications")
        
        return len(notifications) > 0
    except Exception as e:
        print(f"✗ Error retrieving user notifications: {str(e)}")
        return False


def test_mark_as_read(notification_id):
    """Test marking a notification as read"""
    print("\n=== Testing Mark as Read ===")
    
    try:
        db = get_firestore_client()
        
        # Mark notification as read
        success = mark_notification_as_read(db, notification_id)
        
        if success:
            print(f"✓ Notification marked as read")
            
            # Verify it was marked as read
            notification = get_notification_by_id(db, notification_id)
            if notification and notification.read:
                print(f"✓ Verified notification is marked as read")
                return True
            else:
                print(f"✗ Notification read status not updated")
                return False
        else:
            print(f"✗ Failed to mark notification as read")
            return False
    except Exception as e:
        print(f"✗ Error marking notification as read: {str(e)}")
        return False


def test_unread_count():
    """Test getting unread notification count"""
    print("\n=== Testing Unread Count ===")
    
    try:
        db = get_firestore_client()
        
        # Get unread count
        count = get_unread_count(db, "test_user_123")
        
        print(f"✓ Unread count: {count}")
        return True
    except Exception as e:
        print(f"✗ Error getting unread count: {str(e)}")
        return False


def test_mark_all_as_read():
    """Test marking all notifications as read"""
    print("\n=== Testing Mark All as Read ===")
    
    try:
        db = get_firestore_client()
        
        # Create a few more test notifications
        for i in range(3):
            create_notification(
                db=db,
                user_id="test_user_123",
                notification_type="system_update",
                title=f"Test Notification {i+2}",
                message=f"This is test notification {i+2}"
            )
        
        print(f"✓ Created 3 additional test notifications")
        
        # Mark all as read
        count = mark_all_notifications_as_read(db, "test_user_123")
        
        print(f"✓ Marked {count} notifications as read")
        
        # Verify unread count is 0
        unread_count = get_unread_count(db, "test_user_123")
        if unread_count == 0:
            print(f"✓ Verified unread count is 0")
            return True
        else:
            print(f"✗ Unread count is {unread_count}, expected 0")
            return False
    except Exception as e:
        print(f"✗ Error marking all as read: {str(e)}")
        return False


def test_expired_notifications_cleanup():
    """Test deleting expired notifications"""
    print("\n=== Testing Expired Notifications Cleanup ===")
    
    try:
        db = get_firestore_client()
        
        # Create an expired notification (manually set expiration date in the past)
        notification = Notification(
            user_id="test_user_123",
            notification_type="system_update",
            title="Expired Notification",
            message="This notification should be deleted",
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        )
        
        # Save to Firestore
        db.collection('notifications').document(notification.notification_id).set(notification.to_dict())
        print(f"✓ Created expired test notification")
        
        # Run cleanup
        deleted_count = delete_expired_notifications(db)
        
        print(f"✓ Deleted {deleted_count} expired notifications")
        
        # Verify the expired notification was deleted
        retrieved = get_notification_by_id(db, notification.notification_id)
        if retrieved is None:
            print(f"✓ Verified expired notification was deleted")
            return True
        else:
            print(f"✗ Expired notification still exists")
            return False
    except Exception as e:
        print(f"✗ Error testing cleanup: {str(e)}")
        return False


def cleanup_test_data():
    """Clean up test notifications"""
    print("\n=== Cleaning Up Test Data ===")
    
    try:
        db = get_firestore_client()
        
        # Delete all test notifications
        query = db.collection('notifications').where('userId', '==', 'test_user_123')
        deleted_count = 0
        
        for doc in query.stream():
            doc.reference.delete()
            deleted_count += 1
        
        print(f"✓ Deleted {deleted_count} test notifications")
        return True
    except Exception as e:
        print(f"✗ Error cleaning up test data: {str(e)}")
        return False


def run_all_tests():
    """Run all notification tests"""
    print("\n" + "="*60)
    print("NOTIFICATION FUNCTIONALITY TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Create notification
    notification_id = test_notification_creation()
    results.append(("Notification Creation", notification_id is not None))
    
    if notification_id:
        # Test 2: Retrieve notification
        results.append(("Notification Retrieval", test_notification_retrieval(notification_id)))
        
        # Test 3: Get user notifications
        results.append(("User Notifications", test_user_notifications()))
        
        # Test 4: Mark as read
        results.append(("Mark as Read", test_mark_as_read(notification_id)))
        
        # Test 5: Unread count
        results.append(("Unread Count", test_unread_count()))
        
        # Test 6: Mark all as read
        results.append(("Mark All as Read", test_mark_all_as_read()))
        
        # Test 7: Expired notifications cleanup
        results.append(("Expired Cleanup", test_expired_notifications_cleanup()))
    
    # Cleanup
    cleanup_test_data()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
