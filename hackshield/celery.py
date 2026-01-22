# hackshield/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackshield.settings')

app = Celery('hackshield')

# Load settings with "CELERY_" prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto discover tasks.py from all installed apps
app.autodiscover_tasks()


# === Add Celery Beat Schedules ===
app.conf.beat_schedule = {
    # 🕛 Reset user streaks daily at midnight
    'reset-streaks-daily': {
        'task': 'core.tasks.reset_streaks',
        'schedule': crontab(hour=0, minute=0),
    },
    # Optional example: generate daily missions at 6 AM
    # 'daily-mission-generation': {
    #     'task': 'core.tasks.generate_daily_missions',
    #     'schedule': crontab(hour=6, minute=0),
    # },
}

app.conf.timezone = 'Asia/Kolkata'  # ✅ adjust to your local timezone
