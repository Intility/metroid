import json
import logging

import requests
from decouple import config
from django.utils import timezone

from demoproj.celery import app
from metro.celery import MetroTask

logger = logging.getLogger(__name__)


@app.task(base=MetroTask)
def my_func(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
    """
    Demo task
    """
    logger.info(
        'Message %s, topic %s, subscription_name %s, subject: %s', message, topic_name, subscription_name, subject
    )
    if subject == 'jonas/tests':
        r = requests.post(
            'https://api.intility.no/metro/snt-demo',
            headers={'content-type': 'application/json', 'x-metro-key': config('PUBLISH_METRO_KEY')},
            data=json.dumps(
                {
                    'eventType': 'Intility.Jonas.Testing',
                    'eventTime': timezone.now().isoformat(),
                    'dataVersion': '1.0',
                    'data': {'content': 'Yo mister!'},
                    'subject': 'jonas/tests',
                }
            ),
        )
        r.raise_for_status()
        logger.info('POSTED! %s', r.status_code)
    return
