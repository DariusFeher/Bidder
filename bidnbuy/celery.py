import os

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from celery.schedules import crontab




# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bidnbuy.settings')

app = Celery('bidnbuy')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-minute-task': {
        'task': 'bidnbuy.tasks.send_email_task',
        'schedule': crontab(),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# @app.task(bind=True)
# def send_email_task(self):
#     send_mail(
#         'Celery task worked!',
#         'this is proof that is working',
#         settings.EMAIL_FROM_USER,
#         ['dariusmarian51@yahoo.com']
#     )
#     return None

