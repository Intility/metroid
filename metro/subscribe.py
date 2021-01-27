import json
import logging
from typing import Callable, Union

from asgiref.sync import sync_to_async
from azure.servicebus import ServiceBusReceivedMessage, TransportType
from azure.servicebus.aio import ServiceBusClient, ServiceBusReceiver

from metro.typing import Handler

logger = logging.getLogger('metro')


async def subscribe_to_topic(
    connection_string: str,
    topic_name: str,
    subscription_name: str,
    handlers: Union[list[Handler], list[dict[str, Union[str, Callable]]]],
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
                    if handler.get('subject') == loaded_message.get('subject'):
                        logger.info('Subject matching: %s', handler.get('subject'))
                        await receiver.defer_message(message=message)
                        handled_message = True
                        logger.info('Message with sequence number %s deferred', sequence_number)
                        await sync_to_async(handler.get('handler_function').apply_async)(  # type: ignore
                            kwargs={
                                'message': loaded_message,
                                'topic_name': topic_name,
                                'subscription_name': subscription_name,
                                'sequence_number': sequence_number,
                            }
                        )
                        logger.info('Celery task started')
                if not handled_message:
                    logger.info('Completing message')
                    await receiver.complete_message(message=message)
