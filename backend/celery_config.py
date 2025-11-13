"""
Celery Configuration for Background Task Processing
Handles ML model training, threat prediction, and blockchain operations
"""

import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery(
    'zero_trust_ai',
    broker=os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Celery Configuration
celery_app.conf.update(
    # Task Settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task Execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result Backend
    result_expires=86400,  # 24 hours
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Broker Settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Worker Settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat Schedule (Periodic Tasks)
    beat_schedule={
        # Monitor active sessions every 30 seconds
        'monitor-active-sessions': {
            'task': 'app.tasks.session_monitoring_tasks.monitor_active_sessions',
            'schedule': 30.0,  # Every 30 seconds
        },
        # Train behavioral models daily at 2 AM
        'train-behavioral-models': {
            'task': 'app.tasks.ml_tasks.train_behavioral_models',
            'schedule': crontab(hour=2, minute=0),
        },
        # Generate threat predictions every 6 hours
        'generate-threat-predictions': {
            'task': 'app.tasks.threat_prediction_tasks.generate_threat_predictions',
            'schedule': crontab(minute=0, hour='*/6'),
        },
        # Run threat detections every hour
        'run-threat-detections': {
            'task': 'app.tasks.threat_prediction_tasks.run_threat_detections',
            'schedule': crontab(minute=0),
        },
        # Calculate prediction accuracy daily at 4 AM
        'calculate-prediction-accuracy': {
            'task': 'app.tasks.threat_prediction_tasks.calculate_prediction_accuracy',
            'schedule': crontab(hour=4, minute=0),
        },
        # Optimize policies daily at 3 AM
        'optimize-policies': {
            'task': 'app.tasks.policy_tasks.optimize_policies',
            'schedule': crontab(hour=3, minute=0),
        },
        # Check policy health every 6 hours
        'check-policy-health': {
            'task': 'app.tasks.policy_tasks.check_policy_health',
            'schedule': crontab(minute=0, hour='*/6'),
        },
        # Cleanup old sessions every hour
        'cleanup-expired-sessions': {
            'task': 'app.tasks.cleanup_tasks.cleanup_expired_sessions',
            'schedule': crontab(minute=0),
        },
        # Cleanup old behavioral data weekly on Monday at 1 AM
        'cleanup-old-behavioral-data': {
            'task': 'app.tasks.cleanup_tasks.cleanup_old_behavioral_data',
            'schedule': crontab(hour=1, minute=0, day_of_week=1),
        },
        # Cleanup old threat predictions weekly on Tuesday at 1 AM
        'cleanup-old-threat-predictions': {
            'task': 'app.tasks.cleanup_tasks.cleanup_old_threat_predictions',
            'schedule': crontab(hour=1, minute=0, day_of_week=2),
        },
        # Cleanup old notifications daily at 5 AM
        'cleanup-old-notifications': {
            'task': 'app.tasks.cleanup_tasks.cleanup_old_notifications',
            'schedule': crontab(hour=5, minute=0),
        },
        # Cleanup cache every 6 hours
        'cleanup-cache': {
            'task': 'app.tasks.cleanup_tasks.cleanup_cache',
            'schedule': crontab(minute=0, hour='*/6'),
        },
        # Generate system health report daily at 6 AM
        'generate-system-health-report': {
            'task': 'app.tasks.cleanup_tasks.generate_system_health_report',
            'schedule': crontab(hour=6, minute=0),
        },
        # Update threat models weekly on Sunday at 1 AM
        'update-threat-models': {
            'task': 'app.tasks.ml_tasks.update_threat_models',
            'schedule': crontab(hour=1, minute=0, day_of_week=0),
        },
        # Cleanup old ML models weekly on Wednesday at 1 AM
        'cleanup-old-models': {
            'task': 'app.tasks.ml_tasks.cleanup_old_models',
            'schedule': crontab(hour=1, minute=0, day_of_week=3),
        },
        # Sync blockchain audit trail every 5 minutes
        'sync-blockchain-audit': {
            'task': 'app.tasks.blockchain_tasks.sync_audit_trail',
            'schedule': crontab(minute='*/5'),
        },
        # Check blockchain health every hour
        'check-blockchain-health': {
            'task': 'app.tasks.blockchain_tasks.check_blockchain_health',
            'schedule': crontab(minute=0),
        },
        # Cleanup old blockchain records monthly on 1st at 2 AM
        'cleanup-old-blockchain-records': {
            'task': 'app.tasks.blockchain_tasks.cleanup_old_blockchain_records',
            'schedule': crontab(hour=2, minute=0, day_of_month=1),
        },
    },
)

# Task Routes
celery_app.conf.task_routes = {
    'app.tasks.ml_tasks.*': {'queue': 'ml_queue'},
    'app.tasks.blockchain_tasks.*': {'queue': 'blockchain_queue'},
    'app.tasks.policy_tasks.*': {'queue': 'policy_queue'},
    'app.tasks.cleanup_tasks.*': {'queue': 'default'},
}

# Import tasks to register them
celery_app.autodiscover_tasks(['app.tasks'])
