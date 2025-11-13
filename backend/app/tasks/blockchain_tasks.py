"""
Celery Tasks for Blockchain Audit Trail
Background tasks for recording events to blockchain and syncing audit trail
"""

from celery_config import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.blockchain_tasks.record_audit_event')
def record_audit_event(event_type: str, event_data: dict):
    """
    Record a critical security event to blockchain
    Called asynchronously to avoid blocking main request flow
    
    Args:
        event_type: Type of event (access_grant, access_deny, policy_change, etc.)
        event_data: Event data to record
    """
    try:
        from app.services.blockchain_service import blockchain_service
        
        # Record to blockchain
        result = blockchain_service.record_to_blockchain(event_type, event_data)
        
        if result.get('success'):
            logger.info(f"Recorded {event_type} to blockchain: tx {result.get('tx_hash')}")
        else:
            logger.error(f"Failed to record {event_type} to blockchain: {result.get('error')}")
        
        return {
            'status': 'success' if result.get('success') else 'failed',
            'event_type': event_type,
            'tx_hash': result.get('tx_hash'),
            'block_number': result.get('block_number'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording audit event to blockchain: {e}")
        return {
            'status': 'error',
            'event_type': event_type,
            'error': str(e)
        }


@celery_app.task(name='app.tasks.blockchain_tasks.sync_audit_trail')
def sync_audit_trail():
    """
    Sync pending audit events to blockchain
    Runs every 5 minutes (configured in celery_config.py)
    Processes queued events that failed to record immediately
    """
    try:
        logger.info("Starting blockchain audit trail sync...")
        
        from app.services.blockchain_service import blockchain_service
        from app.models.audit_log import AuditLog
        
        # Get pending audit events (events not yet on blockchain)
        # In production, query Firestore for pending events
        # pending_events = AuditLog.get_pending_blockchain_events()
        
        events_synced = 0
        events_failed = 0
        
        # For each pending event, try to record to blockchain
        # for event in pending_events:
        #     try:
        #         result = blockchain_service.record_to_blockchain(
        #             event.event_type,
        #             event.to_dict()
        #         )
        #         
        #         if result.get('success'):
        #             # Update event with blockchain info
        #             event.update_blockchain_info(
        #                 tx_hash=result.get('tx_hash'),
        #                 block_number=result.get('block_number')
        #             )
        #             events_synced += 1
        #         else:
        #             events_failed += 1
        #             
        #     except Exception as e:
        #         logger.error(f"Failed to sync event {event.id}: {e}")
        #         events_failed += 1
        
        logger.info(f"Blockchain sync completed: {events_synced} synced, {events_failed} failed")
        
        return {
            'status': 'success',
            'events_synced': events_synced,
            'events_failed': events_failed,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sync_audit_trail task: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='app.tasks.blockchain_tasks.verify_audit_integrity')
def verify_audit_integrity(record_id: str):
    """
    Verify the integrity of a specific audit record
    Can be triggered on-demand
    
    Args:
        record_id: Audit record identifier
    """
    try:
        logger.info(f"Verifying audit integrity for record {record_id}...")
        
        from app.services.blockchain_service import blockchain_service
        
        # Verify the record
        result = blockchain_service.verify_audit_integrity(record_id)
        
        if not result.get('verified'):
            logger.warning(f"Audit record {record_id} failed integrity check!")
            
            # Send alert to admins
            from websocket_config import emit_admin_notification
            emit_admin_notification({
                'type': 'audit_integrity_alert',
                'severity': 'critical',
                'message': f'Audit record {record_id} failed integrity verification',
                'record_id': record_id,
                'details': result
            })
        
        return {
            'status': 'success',
            'record_id': record_id,
            'verified': result.get('verified'),
            'details': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error verifying audit integrity: {e}")
        return {
            'status': 'error',
            'record_id': record_id,
            'error': str(e)
        }


@celery_app.task(name='app.tasks.blockchain_tasks.batch_record_events')
def batch_record_events(events: list):
    """
    Record multiple events to blockchain in a single transaction
    More efficient for high-frequency events
    
    Args:
        events: List of events to record
    """
    try:
        logger.info(f"Batch recording {len(events)} events to blockchain...")
        
        from app.services.blockchain_service import blockchain_service
        
        # Batch record events
        result = blockchain_service.batch_record_events(events)
        
        logger.info(f"Batch recorded {result.get('events_recorded')} events")
        
        return {
            'status': 'success',
            'events_recorded': result.get('events_recorded'),
            'tx_hash': result.get('tx_hash'),
            'block_number': result.get('block_number'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error batch recording events: {e}")
        return {
            'status': 'error',
            'events_count': len(events),
            'error': str(e)
        }


@celery_app.task(name='app.tasks.blockchain_tasks.store_large_data_ipfs')
def store_large_data_ipfs(data: dict, metadata: dict = None):
    """
    Store large audit data on IPFS and record CID on blockchain
    
    Args:
        data: Large data to store
        metadata: Optional metadata
    """
    try:
        logger.info("Storing large data on IPFS...")
        
        from app.services.blockchain_service import blockchain_service
        
        # Store on IPFS
        result = blockchain_service.store_large_data_ipfs(data)
        
        if result.get('success'):
            ipfs_cid = result.get('ipfs_cid')
            
            # Record CID on blockchain
            blockchain_result = blockchain_service.record_ipfs_reference(
                ipfs_cid,
                metadata or {}
            )
            
            logger.info(f"Stored data on IPFS: {ipfs_cid}")
            
            return {
                'status': 'success',
                'ipfs_cid': ipfs_cid,
                'tx_hash': blockchain_result.get('tx_hash'),
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Failed to store data on IPFS: {result.get('error')}")
            return {
                'status': 'failed',
                'error': result.get('error')
            }
        
    except Exception as e:
        logger.error(f"Error storing data on IPFS: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@celery_app.task(name='app.tasks.blockchain_tasks.check_blockchain_health')
def check_blockchain_health():
    """
    Check blockchain node health and connectivity
    Runs every hour
    """
    try:
        logger.info("Checking blockchain health...")
        
        from app.services.blockchain_service import blockchain_service
        
        # Check blockchain connection
        health = blockchain_service.check_health()
        
        if not health.get('connected'):
            logger.error("Blockchain node is not connected!")
            
            # Send alert to admins
            from websocket_config import emit_admin_notification
            emit_admin_notification({
                'type': 'blockchain_health_alert',
                'severity': 'high',
                'message': 'Blockchain node is not connected',
                'details': health
            })
        
        logger.info(f"Blockchain health check completed: {health.get('status')}")
        
        return {
            'status': 'success',
            'health': health,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking blockchain health: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@celery_app.task(name='app.tasks.blockchain_tasks.cleanup_old_blockchain_records')
def cleanup_old_blockchain_records():
    """
    Clean up old blockchain record references from database
    Keep blockchain data intact, just clean up local references
    Runs monthly
    """
    try:
        logger.info("Cleaning up old blockchain records...")
        
        # Clean up records older than 1 year
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        
        # In production, archive old records to cold storage
        # and remove from active database
        
        records_archived = 0
        
        # Placeholder for cleanup logic
        # records_archived = archive_old_blockchain_records(cutoff_date)
        
        logger.info(f"Archived {records_archived} old blockchain records")
        
        return {
            'status': 'success',
            'records_archived': records_archived,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up blockchain records: {e}")
        return {'status': 'error', 'error': str(e)}
