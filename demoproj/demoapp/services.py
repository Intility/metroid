import logging

from asgiref.sync import sync_to_async
from demoproj.celery import app
import requests
from django.utils import timezone
from decouple import config

from metro.complete import complete_deferred_message
import json

logger = logging.getLogger(__name__)


@app.task
def my_func(*, message: dict, topic_name: str, subscription_name: str, sequence_number: int) -> None:
    """
    Demo task
    """
    logger.info(f'Got message {message}')
    logger.info(f'Topic: {topic_name}')
    logger.info(f'Subscription name: {subscription_name}')
    logger.info(f'Sequence number: {sequence_number}')
    if message.get('subject') == 'jonas/tests':
        r = requests.post(
            'https://api.intility.no/metro/snt-demo',
            headers={'content-type': 'application/json', 'x-metro-key': config('PUBLISH_METRO_KEY')},
            data=json.dumps(
                {
                    'eventType': 'Intility.Jonas.Testing',
                    'eventTime': timezone.now().isoformat(),
                    'dataVersion': '1.0',
                    'data': {'content': 'from or(g!'},
                    'subject': 'jonas/tests',
                }
            ),
        )
        logger.info('POSTED! %s', r.status_code)
    sync_to_async(complete_deferred_message)(
        sequence_number=sequence_number, topic_name=topic_name, subscription_name=subscription_name
    )
    return
