import json
import logging

from django.utils import timezone

import requests
from decouple import config
from demoproj.celery import app

from metroid import MetroidTask

logger = logging.getLogger(__name__)


@app.task(base=MetroidTask)
def my_func(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
    """
    Demo task
    """
    logger.info(
        'Message %s, topic %s, subscription_name %s, subject: %s', message, topic_name, subscription_name, subject
    )
    if subject == 'Test/Django/Module':
        response = requests.post(
            url=config('PUBLISH_METRO_URL'),
            headers={'content-type': 'application/json', 'x-metro-key': config('PUBLISH_METRO_KEY')},
            data=json.dumps(
                {
                    'eventType': 'Intility.Jonas.Testing',
                    'eventTime': timezone.now().isoformat(),
                    'dataVersion': '1.0',
                    'data': {'content': 'Yo, Metro is awesome'},
                    'subject': 'Test/Django/Module',
                }
            ),
        )
        response.raise_for_status()
        logger.info('POSTED! %s', response.status_code)
    return


@app.task(base=MetroidTask)
def my_broken_task(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
    """
    Broken demo task
    """
    raise ValueError('Oops, an exception happened! You can retry this task in the admin Dashboard :-)')
