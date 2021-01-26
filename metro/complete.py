import logging

from azure.servicebus.aio import ServiceBusClient, ServiceBusReceiver

logger = logging.getLogger('metro')


async def complete_deferred_message(*, sequence_number: int, topic_name: str, subscription_name: str) -> None:
    """
    Completes a message based on sequence number, topic name and subscription name.

    :param sequence_number: Sequence number of the message
    :param topic_name: Topic name
    :param subscription_name: Subscription name
    """
    from metro.config import settings

    connection_string = settings.get_subscription_string(topic_name=topic_name, subscription_name=subscription_name)
    metro_client: ServiceBusClient
    async with ServiceBusClient.from_connection_string(conn_str=connection_string) as metro_client:
        # Use the topic name and subscription name to start a receiver.
        receiver: ServiceBusReceiver
        async with metro_client.get_subscription_receiver(
            topic_name=topic_name, subscription_name=subscription_name
        ) as receiver:
            logger.info('Deferring message with sequence number %s', sequence_number)
            messages = await receiver.receive_deferred_messages(sequence_numbers=sequence_number)
            await receiver.complete_message(message=messages[0])
