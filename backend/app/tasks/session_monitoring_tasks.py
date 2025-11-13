"""
Celery Tasks for Session Monitoring
Periodic tasks to monitor behavioral risk scores
"""

from celery_config import celery_app
from app.services.session_monitor import session_monitor
from app.models.behavioral_session import BehavioralSession
from datetime import datetime, timedelta


@celery_app.task(name='app.tasks.session_monitoring_tasks.monitor_active_sessions')
def monitor_active_sessions():
    """
    Monitor all active sessions for behavioral risk
    Runs every 30 seconds (configured in celery_config.py)
    """
    try:
        print("Starting active session monitoring...")
        
        # Get all sessions active in the last 5 minutes
        # In a real implementation, you would query Firestore for active sessions
        # For now, this is a placeholder
        
        session_monitor.monitor_all_active_sessions()
        
        print("Active session monitoring completed")
        return {'status': 'success', 'timestamp': datetime.utcnow().isoformat()}
        
    except Exception as e:
        print(f"Error in monitor_active_sessions task: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='app.tasks.session_monitoring_tasks.check_session_risk')
def check_session_risk(user_id: str, session_id: str):
    """
    Check risk score for a specific session
    Can be called on-demand or scheduled
    """
    try:
        result = session_monitor.check_session_risk(user_id, session_id)
        return {
            'status': 'success',
            'user_id': user_id,
            'session_id': session_id,
            'result': result
        }
        
    except Exception as e:
        print(f"Error checking session risk: {e}")
        return {
            'status': 'error',
            'user_id': user_id,
            'session_id': session_id,
            'error': str(e)
        }
