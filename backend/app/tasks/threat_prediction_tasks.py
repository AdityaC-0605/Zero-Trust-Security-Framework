"""
Celery Tasks for Threat Prediction
Periodic tasks to generate and track threat predictions
"""

from celery_config import celery_app
from app.services.threat_predictor import threat_predictor
from datetime import datetime


@celery_app.task(name='app.tasks.threat_prediction_tasks.generate_threat_predictions')
def generate_threat_predictions():
    """
    Generate threat predictions for all users with suspicious activity
    Runs every 6 hours (configured in celery_config.py)
    """
    try:
        print("Starting threat prediction generation...")
        
        # Generate predictions
        predictions = threat_predictor.predict_threats()
        
        # Send admin alerts for high confidence predictions
        alert_count = 0
        for prediction in predictions:
            if prediction.get('confidence', 0) >= 0.80:
                if threat_predictor.send_admin_alert(prediction):
                    alert_count += 1
        
        print(f"Generated {len(predictions)} predictions, sent {alert_count} admin alerts")
        
        return {
            'status': 'success',
            'predictions_generated': len(predictions),
            'admin_alerts_sent': alert_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error in generate_threat_predictions task: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='app.tasks.threat_prediction_tasks.run_threat_detections')
def run_threat_detections():
    """
    Run all threat detection algorithms
    Runs every hour
    """
    try:
        print("Running threat detection algorithms...")
        
        # Run all detections
        detections = threat_predictor.run_all_detections()
        
        # Log detections
        from app.services.audit_logger import log_audit_event
        
        for detection in detections:
            log_audit_event(
                user_id='system',
                action='threat_detected',
                resource_type='security_threat',
                resource_id=detection.get('threat_type'),
                details=detection,
                severity=detection.get('severity', 'medium')
            )
        
        print(f"Detected {len(detections)} threats")
        
        return {
            'status': 'success',
            'detections': len(detections),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error in run_threat_detections task: {e}")
        return {'status': 'error', 'error': str(e)}


@celery_app.task(name='app.tasks.threat_prediction_tasks.calculate_prediction_accuracy')
def calculate_prediction_accuracy():
    """
    Calculate and log prediction accuracy
    Runs daily
    """
    try:
        print("Calculating prediction accuracy...")
        
        # Calculate accuracy for last 30 days
        accuracy = threat_predictor.calculate_prediction_accuracy(days=30)
        
        # Log accuracy metrics
        from app.services.audit_logger import log_audit_event
        
        log_audit_event(
            user_id='system',
            action='prediction_accuracy_calculated',
            resource_type='ml_metrics',
            resource_id='threat_prediction_accuracy',
            details=accuracy
        )
        
        print(f"Prediction accuracy: {accuracy.get('accuracy', 0)}%")
        
        # Check if accuracy is below threshold
        if accuracy.get('accuracy', 0) < 80:
            print("WARNING: Prediction accuracy below 80% threshold")
            # Could trigger model retraining here
        
        return {
            'status': 'success',
            'accuracy': accuracy,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error in calculate_prediction_accuracy task: {e}")
        return {'status': 'error', 'error': str(e)}
