from metroid.celery import MetroidTask  # noqa F401
from metroid.publish import publish_event  # noqa F401

__version__ = '1.0.1'
default_app_config = 'metroid.apps.MetroidConfig'