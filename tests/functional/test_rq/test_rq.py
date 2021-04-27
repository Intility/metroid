from django.test import override_settings
from django.utils.module_loading import import_string

import django_rq
import pytest

from metroid.models import FailedMessage
from metroid.rq import on_failure
from rq import SimpleWorker


@pytest.mark.django_db
def test_faulty_metro_data():
    assert FailedMessage.objects.count() == 0
    with override_settings(RQ_QUEUES={'metroid': {}, 'fake': {}}):
        a_random_task = import_string('demoproj.tasks.a_random_task')
        queue = django_rq.get_queue('metroid')
        queue.enqueue(
            a_random_task,
            job_id='5F9914AB-2CC1-4A57-9A67-8586ADC2D8B6',
            kwargs={
                'message': {'hello': 'world'},
                'topic_name': 'mocked_topic',
                'subscription_name': 'mocked_subscription',
                'subject': 'mocked_subject',
            },
        )
        worker = SimpleWorker([queue], connection=queue.connection, exception_handlers=[on_failure])
        worker.work(burst=True)

    assert FailedMessage.objects.count() == 1


@pytest.mark.django_db
def test_non_metroid_task():
    assert FailedMessage.objects.count() == 0
    with override_settings(RQ_QUEUES={'metroid': {}, 'fake': {}}):
        a_random_task = import_string('demoproj.tasks.a_random_task')
        queue = django_rq.get_queue('fake')
        queue.enqueue(
            a_random_task,
            job_id='5F9914AB-2CC1-4A57-9A67-8586ADC2D8B6',
            kwargs={
                'message': {'hello': 'world'},
                'topic_name': 'mocked_topic',
                'subscription_name': 'mocked_subscription',
                'subject': 'mocked_subject',
            },
        )
        worker = SimpleWorker([queue], connection=queue.connection, exception_handlers=[on_failure])
        worker.work(burst=True)

    assert FailedMessage.objects.count() == 0
