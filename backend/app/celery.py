"""
Celery configuration for YYC³ EasyVizAI
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('easyvizai')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Schedule periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-learning-loop': {
        'task': 'app.core.tasks.daily_learning_loop_task',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9:00 AM
    },
    'extract-knowledge-points': {
        'task': 'app.core.tasks.extract_knowledge_points_task',
        'schedule': crontab(hour=8, minute=30),  # Daily at 8:30 AM
    },
    'cleanup-old-data': {
        'task': 'app.core.tasks.cleanup_old_data_task',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Weekly on Sunday at 2:00 AM
        'kwargs': {'days_to_keep': 90}
    },
}

app.conf.timezone = 'Asia/Shanghai'