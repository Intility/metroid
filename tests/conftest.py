from django.test import override_settings

import pytest
from tests.functional.mock_service_bus import instance_service_mock_error, instance_service_mock_ok

from metroid.config import Settings


@pytest.fixture
def mock_service_bus_client_ok(mocker):
    return mocker.patch('metroid.subscribe.ServiceBusClient', instance_service_mock_ok())


@pytest.fixture
def mock_service_bus_client_failure(mocker):
    return mocker.patch('metroid.subscribe.ServiceBusClient', instance_service_mock_error())


@pytest.fixture(autouse=True)
def mock_subscriptions(monkeypatch):
    """
    Default settings
    """
    with override_settings(
        METROID={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'sub-test-djangomoduletest',
                    'connection_string': 'my long connection string',
                    'handlers': [
                        {'subject': 'Test/Django/Module', 'handler_function': 'demoproj.demoapp.services.my_func'},
                        {
                            'subject': 'Exception/Django/Module',
                            'handler_function': 'demoproj.demoapp.services.my_broken_task',
                        },
                    ],
                },
                {
                    'topic_name': 'test-two',
                    'subscription_name': 'sub-test-test2',
                    'connection_string': 'my long connection string',
                    'handlers': [
                        {
                            'subject': 'Exception/Django/Module',
                            'handler_function': 'demoproj.demoapp.services.my_broken_task',
                        },
                    ],
                },
            ],
            'publish_settings': [
                {
                    'topic_name': 'test123',
                    'x_metro_key': 'my-metro-key',
                }
            ],
        },
    ):
        settings = Settings()
        monkeypatch.setattr('metroid.management.commands.metroid.settings', settings)
        monkeypatch.setattr('metroid.publish.settings', settings)
        monkeypatch.setattr('metroid.republish.settings', settings)
