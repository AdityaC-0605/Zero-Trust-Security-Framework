"""
Celery Tasks Package
Contains background tasks for ML training, threat prediction, and policy optimization
"""

# Import all tasks to register them with Celery
from app.tasks.ml_tasks import (
    train_behavioral_models,
    update_threat_models,
    train_user_behavioral_model,
    update_behavioral_baseline,
    cleanup_old_models
)

from app.tasks.policy_tasks import (
    optimize_policies,
    calculate_policy_effectiveness,
    track_policy_outcome,
    simulate_policy_change,
    rollback_policy,
    check_policy_health
)

from app.tasks.blockchain_tasks import (
    record_audit_event,
    sync_audit_trail,
    verify_audit_integrity,
    batch_record_events,
    store_large_data_ipfs,
    check_blockchain_health,
    cleanup_old_blockchain_records
)

from app.tasks.session_monitoring_tasks import (
    monitor_active_sessions,
    check_session_risk
)

from app.tasks.threat_prediction_tasks import (
    generate_threat_predictions,
    run_threat_detections,
    calculate_prediction_accuracy
)

from app.tasks.cleanup_tasks import (
    cleanup_expired_sessions,
    cleanup_old_behavioral_data,
    cleanup_old_threat_predictions,
    cleanup_old_notifications,
    cleanup_cache,
    generate_system_health_report
)

__all__ = [
    # ML Tasks
    'train_behavioral_models',
    'update_threat_models',
    'train_user_behavioral_model',
    'update_behavioral_baseline',
    'cleanup_old_models',
    
    # Policy Tasks
    'optimize_policies',
    'calculate_policy_effectiveness',
    'track_policy_outcome',
    'simulate_policy_change',
    'rollback_policy',
    'check_policy_health',
    
    # Blockchain Tasks
    'record_audit_event',
    'sync_audit_trail',
    'verify_audit_integrity',
    'batch_record_events',
    'store_large_data_ipfs',
    'check_blockchain_health',
    'cleanup_old_blockchain_records',
    
    # Session Monitoring Tasks
    'monitor_active_sessions',
    'check_session_risk',
    
    # Threat Prediction Tasks
    'generate_threat_predictions',
    'run_threat_detections',
    'calculate_prediction_accuracy',
    
    # Cleanup Tasks
    'cleanup_expired_sessions',
    'cleanup_old_behavioral_data',
    'cleanup_old_threat_predictions',
    'cleanup_old_notifications',
    'cleanup_cache',
    'generate_system_health_report'
]
