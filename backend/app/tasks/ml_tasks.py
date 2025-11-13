"""
Celery Tasks for ML Model Training and Updates
Background tasks for training behavioral models and updating threat models
"""

from celery_config import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.ml_tasks.train_behavioral_models')
def train_behavioral_models():
    """
    Train behavioral biometrics models for all users with sufficient data
    Runs daily at 2 AM (configured in celery_config.py)
    """
    try:
        logger.info("Starting behavioral model training...")
        
        from app.services.behavioral_biometrics import behavioral_service
        from app.models.user import User
        
        # Get all users who need model training
        # (users with 2+ weeks of data and no recent model)
        users_trained = 0
        users_failed = 0
        
        # In production, query Firestore for users needing training
        # For now, this is a placeholder structure
        
        # Example: Get users from database
        # users = User.get_users_needing_training()
        
        # For each user, train their model
        # for user in users:
        #     try:
        #         result = behavioral_service.train_user_model(user.id)
        #         if result.get('success'):
        #             users_trained += 1
        #         else:
        #             users_failed += 1
        #     except Exception as e:
        #         logger.error(f"Failed to train model for user {user.id}: {e}")
        #         users_failed += 1
        
        logger.info(f"Behavioral model training completed: {users_trained} trained, {users_failed} failed")
        
        return {
            'status': 'success',
            'users_trained': users_trained,
            'users_failed': users_failed,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in train_behavioral_models task: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='app.tasks.ml_tasks.update_threat_models')
def update_threat_models():
    """
    Update threat prediction models with new data
    Runs weekly on Sunday at 1 AM (configured in celery_config.py)
    """
    try:
        logger.info("Starting threat model update...")
        
        from app.services.threat_predictor import threat_predictor
        
        # Retrain threat prediction models with recent data
        result = threat_predictor.retrain_models()
        
        # Log model performance
        from app.services.audit_logger import log_audit_event
        
        log_audit_event(
            user_id='system',
            action='ml_model_updated',
            resource_type='ml_model',
            resource_id='threat_prediction_model',
            details={
                'model_version': result.get('model_version'),
                'training_samples': result.get('training_samples'),
                'accuracy': result.get('accuracy'),
                'precision': result.get('precision'),
                'recall': result.get('recall')
            }
        )
        
        logger.info(f"Threat model updated: version {result.get('model_version')}, accuracy {result.get('accuracy')}%")
        
        return {
            'status': 'success',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in update_threat_models task: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='app.tasks.ml_tasks.train_user_behavioral_model')
def train_user_behavioral_model(user_id: str):
    """
    Train behavioral model for a specific user
    Can be triggered on-demand when user has sufficient data
    
    Args:
        user_id: User identifier
    """
    try:
        logger.info(f"Training behavioral model for user {user_id}...")
        
        from app.services.behavioral_biometrics import behavioral_service
        
        # Train the model
        result = behavioral_service.train_user_model(user_id)
        
        if result.get('success'):
            # Cache the trained model
            from app.services.cache_service import cache_service
            cache_service.cache_behavioral_model(
                user_id,
                result.get('model_data'),
                ttl=3600  # 1 hour
            )
            
            logger.info(f"Successfully trained model for user {user_id}")
        else:
            logger.warning(f"Failed to train model for user {user_id}: {result.get('error')}")
        
        return {
            'status': 'success' if result.get('success') else 'failed',
            'user_id': user_id,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training model for user {user_id}: {e}")
        return {
            'status': 'error',
            'user_id': user_id,
            'error': str(e)
        }


@celery_app.task(name='app.tasks.ml_tasks.update_behavioral_baseline')
def update_behavioral_baseline(user_id: str):
    """
    Update user's behavioral baseline with recent data
    Can be triggered periodically or on-demand
    
    Args:
        user_id: User identifier
    """
    try:
        logger.info(f"Updating behavioral baseline for user {user_id}...")
        
        from app.services.behavioral_biometrics import behavioral_service
        
        # Update baseline
        result = behavioral_service.update_baseline(user_id)
        
        if result.get('success'):
            # Cache the updated baseline
            from app.services.cache_service import cache_service
            cache_service.cache_behavioral_baseline(
                user_id,
                result.get('baseline_data'),
                ttl=3600  # 1 hour
            )
            
            logger.info(f"Successfully updated baseline for user {user_id}")
        
        return {
            'status': 'success' if result.get('success') else 'failed',
            'user_id': user_id,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating baseline for user {user_id}: {e}")
        return {
            'status': 'error',
            'user_id': user_id,
            'error': str(e)
        }


@celery_app.task(name='app.tasks.ml_tasks.cleanup_old_models')
def cleanup_old_models():
    """
    Clean up old ML models and training data
    Runs weekly
    """
    try:
        logger.info("Starting ML model cleanup...")
        
        # Clean up models older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # In production, query Firestore for old models
        # and delete them to save storage
        
        models_deleted = 0
        
        # Placeholder for cleanup logic
        # models_deleted = cleanup_old_model_versions(cutoff_date)
        
        logger.info(f"Cleaned up {models_deleted} old models")
        
        return {
            'status': 'success',
            'models_deleted': models_deleted,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_models task: {e}")
        return {'status': 'error', 'error': str(e)}
