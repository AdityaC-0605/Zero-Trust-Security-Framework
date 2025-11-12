"""
Test script for analytics endpoint
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.firebase_config import get_firestore_client
from datetime import datetime, timedelta
import uuid

def test_analytics_endpoint():
    """Test the analytics endpoint with sample data"""
    app = create_app()
    
    with app.test_client() as client:
        print("Testing Analytics Endpoint...")
        
        # Note: This test requires authentication
        # In a real scenario, you would need to authenticate first
        
        # Test with different time ranges
        time_ranges = ['day', 'week', 'month']
        
        for time_range in time_ranges:
            print(f"\nTesting with time range: {time_range}")
            
            # Make request (will fail without auth, but tests the endpoint structure)
            response = client.get(
                f'/api/admin/analytics?timeRange={time_range}',
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.get_json()}")
            
            # Expected to get 401 without authentication
            if response.status_code == 401:
                print("✓ Endpoint requires authentication (as expected)")
            elif response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    analytics = data.get('analytics', {})
                    print(f"✓ Analytics data received:")
                    print(f"  - Total Requests: {analytics.get('totalRequests')}")
                    print(f"  - Approval Rate: {analytics.get('approvalRate')}%")
                    print(f"  - Average Confidence: {analytics.get('averageConfidence')}")
                    print(f"  - Requests by Role: {analytics.get('requestsByRole')}")
                    print(f"  - Top Denied Users: {len(analytics.get('topDeniedUsers', []))}")
                else:
                    print(f"✗ Request failed: {data.get('error')}")

def create_sample_data():
    """Create sample access requests for testing"""
    try:
        db = get_firestore_client()
        
        print("\nCreating sample access request data...")
        
        # Sample user IDs
        user_ids = ['user1', 'user2', 'user3']
        roles = ['student', 'faculty', 'admin']
        decisions = ['granted', 'granted_with_mfa', 'denied']
        resources = ['lab_server', 'library_database', 'admin_panel']
        
        # Create 20 sample requests
        for i in range(20):
            request_data = {
                'requestId': str(uuid.uuid4()),
                'userId': user_ids[i % len(user_ids)],
                'userRole': roles[i % len(roles)],
                'requestedResource': resources[i % len(resources)],
                'intent': f'Sample intent for testing analytics {i}',
                'duration': '7 days',
                'urgency': 'medium',
                'decision': decisions[i % len(decisions)],
                'confidenceScore': 50 + (i * 2),  # Varying scores from 50-88
                'confidenceBreakdown': {
                    'roleMatch': 70,
                    'intentClarity': 60,
                    'historicalPattern': 50,
                    'contextValidity': 80,
                    'anomalyScore': 90
                },
                'timestamp': datetime.utcnow() - timedelta(hours=i),
                'ipAddress': '127.0.0.1',
                'deviceInfo': {
                    'userAgent': 'Test Agent',
                    'platform': 'Test Platform'
                }
            }
            
            db.collection('accessRequests').document(request_data['requestId']).set(request_data)
        
        print(f"✓ Created 20 sample access requests")
        
    except Exception as e:
        print(f"✗ Error creating sample data: {str(e)}")

if __name__ == '__main__':
    print("=" * 60)
    print("Analytics Endpoint Test")
    print("=" * 60)
    
    # Uncomment to create sample data
    # create_sample_data()
    
    test_analytics_endpoint()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
