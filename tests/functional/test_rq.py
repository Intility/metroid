import django_rq
from django.test import override_settings
from django.utils.module_loading import import_string

import pytest

from metroid.models import FailedMessage
from metroid.rq import on_failure


@pytest.mark.django_db
def test_faulty_metro_data():
    rq_queues = {
        'metroid': {
            'ASYNC': False,
            'HOST': 'localhost',
            'DB': 0,
            'PORT': 6378,
        }
    }
    rq_exception_handlers = ['metroid.rq.on_failure']
    assert FailedMessage.objects.count() == 0
    with override_settings(RQ_EXCEPTION_HANDLERS=rq_exception_handlers, RQ_QUEUES=rq_queues):
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
            }
        )
    assert FailedMessage.objects.count() == 1
