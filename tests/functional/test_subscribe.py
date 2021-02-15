from django.test import override_settings

import pytest
from azure.servicebus import TransportType
from celery.app import shared_task
from metro.celery import MetroTask
from metro.subscribe import subscribe_to_topic


@shared_task(base=MetroTask)
def my_task(**kwargs):
    return None


@pytest.mark.asyncio
async def test_subscription(caplog, mock_service_bus_client_ok):
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):  # Runs celery in same thread without workers and stuff
        await subscribe_to_topic(
            **{
                'topic_name': 'test',
                'subscription_name': 'sub-test-mocktest',
                'connection_string': 'my long connection string',
                'handlers': [
                    {
                        'subject': 'Test/Django/Module',
                        'regex': False,
                        'handler_function': 'tests.functional.test_subscribe.my_task',
                    },
                    {
                        'subject': 'Exception/Django/Module',
                        'regex': False,
                        'handler_function': 'tests.functional.test_subscribe.my_task',
                    },
                ],
            }
        )
    log_messages = [x.message for x in caplog.records]
    mock_service_bus_client_ok.from_connection_string.assert_called_with(
        conn_str='my long connection string', transport_type=TransportType.AmqpOverWebsocket
    )
    # This is kinda dumb, as it makes us have to rewrite test if order of logs changes, but it's the easiest way to
    # actually confirm logic.
    # We expect two tasks to be started with the two subjects, and three messages to be ignored
    assert 'Started subscription for topic test and subscription sub-test-mocktest' == log_messages[0]
    assert 'Subject matching: Test/Django/Module' == log_messages[2]
    assert 'Task tests.functional.test_subscribe.my_task' in log_messages[5]
    assert 'Subject matching: Exception/Django/Module' == log_messages[11]
    assert 'Task tests.functional.test_subscribe.my_task' in log_messages[14]
    assert len([message for message in log_messages if message == 'No handler found, completing message']) == 3


@pytest.mark.asyncio
async def test_faulty_metro_data(caplog, mock_service_bus_client_failure):
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        await subscribe_to_topic(
            **{
                'topic_name': 'error',  # This triggers an error in the metro data
                'subscription_name': 'sub-test-mocktest',
                'connection_string': 'my long connection string',
                'handlers': [
                    {
                        'subject': 'Test/Django/Module',
                        'regex': False,
                        'handler_function': 'tests.functional.test_subscribe.my_task',
                    },
                    {
                        'subject': 'Exception/Django/Module',
                        'regex': False,
                        'handler_function': 'tests.functional.test_subscribe.my_task',
                    },
                ],
            }
        )
    mock_service_bus_client_failure.from_connection_string.assert_called_with(
        conn_str='my long connection string', transport_type=TransportType.AmqpOverWebsocket
    )
    log_messages = [x.message for x in caplog.records]
    assert len([message for message in log_messages if 'Unable to decode message' in message]) == 1
