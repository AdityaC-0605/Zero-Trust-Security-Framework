#!/bin/bash

# Start Celery Worker and Beat Scheduler
# This script starts the Celery worker for background task processing

echo "Starting Celery worker and beat scheduler..."

# Set environment
export FLASK_ENV=${FLASK_ENV:-development}

# Start Celery worker with beat scheduler
# -A: Application module
# -l: Log level
# --beat: Enable beat scheduler for periodic tasks
# --concurrency: Number of worker processes

celery -A celery_config.celery_app worker \
    --beat \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --time-limit=3600 \
    --soft-time-limit=3300

# Alternative: Start worker and beat separately
# Terminal 1: celery -A celery_config.celery_app worker --loglevel=info --concurrency=4
# Terminal 2: celery -A celery_config.celery_app beat --loglevel=info
