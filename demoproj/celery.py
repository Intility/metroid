import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

if os.name == 'nt':
    # Windows configuration to make celery run ok on Windows
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demoproj.settings')

app = Celery('metroid')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
