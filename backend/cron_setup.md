# Notification Cleanup Cron Job Setup

This document describes how to set up a cron job to automatically clean up expired notifications (older than 30 days).

## Local Development Setup

For local development, you can manually run the cleanup script:

```bash
cd backend
python -m app.tasks.cleanup_notifications
```

## Production Setup (Linux/Unix)

### Option 1: Using crontab

1. Open crontab editor:
```bash
crontab -e
```

2. Add the following line to run cleanup daily at 2 AM:
```
0 2 * * * cd /path/to/backend && /path/to/python -m app.tasks.cleanup_notifications >> /var/log/notification_cleanup.log 2>&1
```

Replace `/path/to/backend` with your actual backend directory path and `/path/to/python` with your Python interpreter path (e.g., `/usr/bin/python3` or your virtual environment's Python).

### Option 2: Using systemd timer (Recommended for modern Linux)

1. Create a service file `/etc/systemd/system/notification-cleanup.service`:
```ini
[Unit]
Description=Clean up expired notifications
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m app.tasks.cleanup_notifications
StandardOutput=journal
StandardError=journal
```

2. Create a timer file `/etc/systemd/system/notification-cleanup.timer`:
```ini
[Unit]
Description=Run notification cleanup daily
Requires=notification-cleanup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. Enable and start the timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable notification-cleanup.timer
sudo systemctl start notification-cleanup.timer
```

4. Check timer status:
```bash
sudo systemctl status notification-cleanup.timer
sudo systemctl list-timers
```

## Cloud Platform Setup

### Google Cloud Run / Cloud Functions

Create a Cloud Scheduler job:

```bash
gcloud scheduler jobs create http notification-cleanup \
  --schedule="0 2 * * *" \
  --uri="https://your-backend-url.run.app/api/admin/cleanup-notifications" \
  --http-method=POST \
  --oidc-service-account-email=your-service-account@project.iam.gserviceaccount.com
```

Then add an endpoint in your backend to trigger the cleanup:

```python
@app.route('/api/admin/cleanup-notifications', methods=['POST'])
@require_admin
def trigger_cleanup():
    from app.tasks.cleanup_notifications import cleanup_expired_notifications
    count = cleanup_expired_notifications()
    return jsonify({'success': True, 'deleted': count}), 200
```

### Render

Use Render's Cron Jobs feature:

1. In your `render.yaml`, add:
```yaml
services:
  - type: cron
    name: notification-cleanup
    env: python
    schedule: "0 2 * * *"
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python -m app.tasks.cleanup_notifications"
```

### Heroku

Use Heroku Scheduler add-on:

1. Add the scheduler:
```bash
heroku addons:create scheduler:standard
```

2. Open scheduler dashboard:
```bash
heroku addons:open scheduler
```

3. Add a new job with command:
```
python -m app.tasks.cleanup_notifications
```

Set frequency to "Daily" at 02:00 UTC.

## Monitoring

To monitor the cleanup job:

1. Check logs:
```bash
# For cron
tail -f /var/log/notification_cleanup.log

# For systemd
journalctl -u notification-cleanup.service -f

# For cloud platforms
# Check platform-specific logging (Cloud Logging, Render logs, etc.)
```

2. Add alerting if cleanup fails or deletes an unusual number of notifications.

## Testing

Test the cleanup script manually:

```bash
cd backend
python -m app.tasks.cleanup_notifications
```

Expected output:
```
Cleanup completed: X expired notifications deleted
```

Where X is the number of notifications older than 30 days that were deleted.
