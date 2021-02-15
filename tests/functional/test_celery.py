import logging

from django.test import override_settings
from django.utils.module_loading import import_string

import pytest
from metro.models import FailedMessage


@pytest.mark.django_db
def test_faulty_metro_data():
    assert FailedMessage.objects.count() == 0
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        a_random_task = import_string('demoproj.tasks.a_random_task')
        a_random_task.apply_async(
            kwargs={
                'message': {'hello': 'world'},
                'topic_name': 'mocked_topic',
                'subscription_name': 'mocked_subscription',
                'subject': 'mocked_subject',
            }
        )
    assert FailedMessage.objects.count() == 1
