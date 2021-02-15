from django.test import override_settings

import pytest
from metro.config import Settings
from tests.mock_service_bus import service_mock, service_mock_error


@pytest.fixture
def mock_service_bus_client_ok(mocker):
    return mocker.patch('metro.subscribe.ServiceBusClient', service_mock)


@pytest.fixture
def mock_service_bus_client_failure(mocker):
    return mocker.patch('metro.subscribe.ServiceBusClient', service_mock_error)


@pytest.fixture(autouse=True)
def mock_subscriptions(monkeypatch):
    with override_settings(
        METRO={
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
            ]
        }
    ):
        settings = Settings()
        monkeypatch.setattr('metro.management.commands.metro.settings', settings)
