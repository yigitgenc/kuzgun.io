"""
Celery app initialization for kuzgun.io.
"""

import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuzgun.settings')

app = Celery('kuzgun')
app.config_from_object('kuzgun.celeryconfig')
app.autodiscover_tasks()
