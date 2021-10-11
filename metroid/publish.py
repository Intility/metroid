import json
import logging
from typing import Optional, Union

from django.utils import timezone

import requests

from metroid.config import settings

logger = logging.getLogger('metroid')


def publish_event(
    *,
    topic_name: str,
    event_type: str,
    data: Union[list, dict],
    subject: str,
    data_version: str,
    event_time: Optional[str] = None,
) -> None:
    """
    Sync helper function to publish metro events based on a topic name.
    Please read the metro docs before publishing event.

    It make a wrapper around this function based on your needs. If you implement posting to Metro at the end
    of your API logic you might want to still return a 200 to the API user, even if a post to Metro should fail.

    :param topic_name: str
        'Intility.MyTopic'
    :param event_type: str
        'My.Event.Created'
    :param data: Union[list, dict] - Any JSON serializable data
        {'hello': 'world}
    :param subject: str
        'test/subject'
    :param data_version: str
        '1.0'
    :param event_time: Optional[str] - A valid ISO-8601 timestamp (YYYY-MM-DDThh:mm:ssZ/YYYY-MM-DDThh:mm:ss±hh:mm..)
        '2021-02-22T12:34:18.216747+00:00'

    :return: None - Metro gives empty response on valid posts
    :raises: requests.exceptions.HTTPError
    """
    formatted_data = {
        'eventType': event_type,
        'eventTime': event_time or timezone.now().isoformat(),
        'dataVersion': data_version,
        'data': data,
        'subject': subject,
    }
    logger.info('Posting event to Metro topic %s. Data: %s', topic_name, formatted_data)

    try:
        metro_response = requests.post(
            url=f'https://api.intility.no/metro/{topic_name}',
            headers={
                'content-type': 'application/json',
                'x-metro-key': settings.get_x_metro_key(topic_name=topic_name),
            },
            data=json.dumps(formatted_data),
        )
        metro_response.raise_for_status()
        logger.info('Posted to metro')
    except Exception as error:
        from metroid.models import FailedPublishMessage

        logger.info('Failed to post to metro. %s', error)

        try:
            FailedPublishMessage.objects.create(
                event_type=event_type,
                event_time=event_time or timezone.now().isoformat(),
                data_version=data_version,
                data=data,
                subject=subject,
                topic_name=topic_name,
            )
            logger.info('Saved failed message to database.')
        # failsafe just in case
        except Exception as error:  # pragma: no cover
            logger.exception('Unable to save Metro message. Error: %s', error)
    return
