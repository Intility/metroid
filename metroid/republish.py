import json
import logging

from django.utils import timezone

import requests

from metroid.config import settings
from metroid.models import FailedPublishMessage

logger = logging.getLogger('metroid')


def retry_failed_published_events() -> None:
    """
    Trys to publish all previously failed messages again.

    It make a wrapper around this function based on your needs. If you implement posting to Metro at the end
    of your API logic you might want to still return a 200 to the API user, even if a post to Metro should fail.

    :return: None - Metro gives empty response on valid posts
    :raises: requests.exceptions.HTTPError
    """
    for message in FailedPublishMessage.objects.all():
        formatted_data = {
            'eventType': message.event_type,
            'eventTime': message.event_time.isoformat() or timezone.now().isoformat(),
            'dataVersion': message.data_version,
            'data': message.data,
            'subject': message.subject,
        }
        logger.info('Posting event to Metro topic %s. Data: %s', message.topic_name, formatted_data)
        try:
            metro_response = requests.post(
                url=f'https://api.intility.no/metro/{message.topic_name}',
                headers={
                    'content-type': 'application/json',
                    'x-metro-key': settings.get_x_metro_key(topic_name=message.topic_name),
                },
                data=json.dumps(formatted_data),
            )
            logger.info('Posted to metro')
            metro_response.raise_for_status()
            message.delete()
        except Exception as error:
            logger.info('Failed to post to metro. %s', error)
