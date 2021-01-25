import json
import logging
from typing import Callable, Union

from asgiref.sync import sync_to_async
from azure.servicebus import ServiceBusReceivedMessage
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
    async with ServiceBusClient.from_connection_string(conn_str=connection_string) as metro_client:
        # Subscribe to a topic with through our subscription name
        receiver: ServiceBusReceiver
        async with metro_client.get_subscription_receiver(
            topic_name=topic_name, subscription_name=subscription_name
        ) as receiver:
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
                        loaded_message,
                        sequence_number,
                        error,
                    )
                # Check how to handle this message
                for handler in handlers:
                    if handler.get('subject') == loaded_message.get('subject'):
                        await sync_to_async(
                            handler.get('handler_function').apply_async,  # type: ignore
                            thread_sensitive=False,
                        )(
                            message=loaded_message,
                            topic_name=topic_name,
                            subscription_name=subscription_name,
                            sequence_number=sequence_number,
                        )
                        await receiver.defer_message(message=message)
                # TODO What do we do with messages we don't care about?
