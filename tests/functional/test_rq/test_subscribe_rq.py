import logging

from django.test import override_settings

import pytest
from azure.servicebus import TransportType

from metroid.config import Settings
from metroid.subscribe import subscribe_to_topic


@pytest.fixture(autouse=True)
def mock_rq_worker(monkeypatch):
    with override_settings(METROID={'worker_type': 'rq'}):
        settings = Settings()
        monkeypatch.setattr('metroid.subscribe.settings', settings)


@pytest.mark.asyncio
async def test_subscription_rq(caplog, mock_service_bus_client_ok):
    with override_settings(RQ_QUEUES={'metroid': {'ASYNC': False}, 'fake': {}}):
        caplog.set_level(logging.INFO)
        await subscribe_to_topic(
            **{
                'topic_name': 'test',
                'subscription_name': 'sub-test-mocktest',
                'connection_string': 'my long connection string',
                'handlers': [
                    {
                        'subject': 'Test/Django/Module',
                        'regex': False,
                        'handler_function': 'demoproj.tasks.my_task',
                    },
                    {
                        'subject': 'Exception/Django/Module',
                        'regex': False,
                        'handler_function': 'demoproj.tasks.my_task',
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
        assert 'RQ task started' in log_messages[3]

        assert 'Subject matching: Exception/Django/Module' == log_messages[6]
        assert 'RQ task started' in log_messages[7]
        assert len([message for message in log_messages if message == 'No handler found, completing message']) == 3


@pytest.mark.asyncio
async def test_faulty_metro_data_rq(caplog, mock_service_bus_client_failure):
    with override_settings(RQ_QUEUES={'metroid': {'ASYNC': False}, 'fake': {}}):
        await subscribe_to_topic(
            **{
                'topic_name': 'error',  # This triggers an error in the metro data
                'subscription_name': 'sub-test-mocktest',
                'connection_string': 'my long connection string',
                'handlers': [
                    {
                        'subject': 'Test/Django/Module',
                        'regex': False,
                        'handler_function': 'demoproj.tasks.my_task',
                    },
                    {
                        'subject': 'Exception/Django/Module',
                        'regex': False,
                        'handler_function': 'demoproj.tasks.my_task',
                    },
                ],
            }
        )
    mock_service_bus_client_failure.from_connection_string.assert_called_with(
        conn_str='my long connection string', transport_type=TransportType.AmqpOverWebsocket
    )
    log_messages = [x.message for x in caplog.records]
    assert len([message for message in log_messages if 'Unable to decode message' in message]) == 1
