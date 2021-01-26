import logging

from asgiref.sync import sync_to_async
from demoproj.celery import app


from metro.complete import complete_deferred_message

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
    sync_to_async(complete_deferred_message)(
        sequence_number=sequence_number, topic_name=topic_name, subscription_name=subscription_name
    )
    return
