import json
import logging
from typing import List

from django.utils.module_loading import import_string

from asgiref.sync import sync_to_async
from azure.servicebus import ServiceBusReceivedMessage, TransportType
from azure.servicebus.aio import ServiceBusClient, ServiceBusReceiver

from metroid.config import settings
from metroid.typing import Handler
from metroid.utils import match_handler_subject

logger = logging.getLogger('metroid')


async def subscribe_to_topic(
    connection_string: str,
    topic_name: str,
    subscription_name: str,
    handlers: List[Handler],
) -> None:
    """
    Subscribe to a topic, with a connection string
    """
    # Create a connection to Metro
    metro_client: ServiceBusClient
    async with ServiceBusClient.from_connection_string(
        conn_str=connection_string, transport_type=TransportType.AmqpOverWebsocket
    ) as metro_client:
        # Subscribe to a topic with through our subscription name
        receiver: ServiceBusReceiver
        async with metro_client.get_subscription_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
        ) as receiver:
            logger.info('Started subscription for topic %s and subscription %s', topic_name, subscription_name)
            # We now have a receiver, we can use this to talk with Metro
            message: ServiceBusReceivedMessage
            async for message in receiver:
                sequence_number: int = message.sequence_number
                loaded_message: dict = {}
                try:
                    loaded_message = json.loads(str(message))
                except Exception as error:
                    # We defer messages with a faulty body, we do not crash.
                    logger.exception(
                        'Unable to decode message %s. Sequence number %s. Error: %s',
                        message,
                        sequence_number,
                        error,
                    )
                # Check how to handle this message
                logger.info(
                    '%s: Received message, sequence number %s. Content: %s',
                    subscription_name,
                    sequence_number,
                    loaded_message,
                )
                handled_message = False
                for handler in handlers:
                    subject = handler['subject']
                    subject_is_regex = handler['regex']
                    message_subject = loaded_message.get('subject', '')

                    if match_handler_subject(
                        subject=subject, message_subject=message_subject, is_regex=subject_is_regex
                    ):
                        logger.info('Subject matching: %s', handler.get('subject'))
                        handler_function = import_string(handler.get('handler_function'))

                        if settings.worker_type == 'celery':
                            await sync_to_async(handler_function.apply_async)(  # type: ignore
                                kwargs={
                                    'message': loaded_message,
                                    'topic_name': topic_name,
                                    'subscription_name': subscription_name,
                                    'subject': subject,
                                }
                            )
                            logger.info('Celery task started')

                        elif settings.worker_type == 'rq':
                            import django_rq

                            queue = django_rq.get_queue('metroid')
                            await sync_to_async(queue.enqueue)(
                                handler_function,
                                job_id=loaded_message.get('id'),
                                kwargs={
                                    'message': loaded_message,
                                    'topic_name': topic_name,
                                    'subscription_name': subscription_name,
                                    'subject': subject,
                                },
                            )
                            logger.info('RQ task started')

                        await receiver.complete_message(message=message)
                        handled_message = True
                        logger.info('Message with sequence number %s completed', sequence_number)
                if not handled_message:
                    logger.info('No handler found, completing message')
                    await receiver.complete_message(message=message)
