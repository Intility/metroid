import logging

from asgiref.sync import sync_to_async
from celery import shared_task

from metro.defer import defer_message

logger = logging.getLogger(__name__)


@shared_task
def my_func(*, message: dict, toppic_name: str, subscription_name: str, sequence_number: int) -> None:
    """
    Demo task
    """
    logger.info(f'Got message {message}')
    logger.info(f'Topic: {toppic_name}')
    logger.info(f'Subscription name: {subscription_name}')
    logger.info(f'Sequence number: {sequence_number}')
    sync_to_async(defer_message)(
        sequence_number=sequence_number, topic_name=toppic_name, subscription_name=subscription_name
    )
    return
