import asyncio

from django.test import override_settings

import pytest
from demoproj.demoapp.services import my_broken_task, my_func
from metro.config import Settings


@pytest.fixture(autouse=True)
def mock_subscriptions(mocker, monkeypatch):
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'sub-test-djangomoduletest',
                    'connection_string': 'my long connection string',
                    'handlers': [
                        {'subject': 'Test/Django/Module', 'handler_function': my_func},
                        {'subject': 'Exception/Django/Module', 'handler_function': my_broken_task},
                    ],
                },
                {
                    'topic_name': 'test-two',
                    'subscription_name': 'sub-test-test2',
                    'connection_string': 'my long connection string',
                    'handlers': [
                        {'subject': 'Exception/Django/Module', 'handler_function': my_broken_task},
                    ],
                },
            ]
        }
    ):
        settings = Settings()
        monkeypatch.setattr('metro.management.commands.metro.settings', settings)
