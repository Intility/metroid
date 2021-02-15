import logging

from django.test import override_settings

import pytest
from celery import shared_task
from metro.celery import MetroTask
from metro.models import FailedMessage


@shared_task(base=MetroTask, name='tests.functional.test_celery.a_random_task')
def a_random_task(*, message: dict, topic_name: str, subscription_name: str, subject: str):
    raise ValueError('My mocked error :)')


@shared_task(base=MetroTask, name='tests.functional.test_celery.error_task')
def error_task(*, message: dict, topic_name: str, subscription_name: str, subject: str):
    lambda x: None


@pytest.mark.django_db
def test_faulty_metro_data():
    assert FailedMessage.objects.count() == 0
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        a_random_task.apply_async(
            kwargs={
                'message': {'hello': 'world'},
                'topic_name': 'mocked_topic',
                'subscription_name': 'mocked_subscription',
                'subject': 'mocked_subject',
            }
        )
    assert FailedMessage.objects.count() == 1
