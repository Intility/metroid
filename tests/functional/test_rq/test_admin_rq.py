from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from django.utils.module_loading import import_string

import django_rq
import pytest

from metroid.config import Settings
from metroid.models import FailedMessage
from metroid.rq import on_failure
from rq import SimpleWorker


@pytest.fixture
def create_and_sign_in_user(client):
    user = User.objects.create_superuser('testuser', 'test@test.com', 'testpw')
    client.login(username='testuser', password='testpw')
    return


@pytest.fixture
def mock_subscriptions_admin(monkeypatch):
    with override_settings(
        METROID={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'sub-test-djangomoduletest',
                    'connection_string': 'my long connection string',
                    'handlers': [
                        {'subject': 'MockedTask', 'handler_function': 'demoproj.tasks.a_random_task'},
                        {'subject': 'ErrorTask', 'handler_function': 'demoproj.tasks.error_task'},
                    ],
                },
            ],
            'worker_type': 'rq',
        },
    ):
        settings = Settings()
        monkeypatch.setattr('metroid.admin.settings', settings)


@pytest.mark.django_db
def test_admin_action_handler_found_rq(client, caplog, create_and_sign_in_user, mock_subscriptions_admin):
    with override_settings(RQ_QUEUES={'metroid': {}, 'fake': {}}):
        # Create a failed task
        a_random_task = import_string('demoproj.tasks.a_random_task')
        queue = django_rq.get_queue('metroid')
        queue.enqueue(
            a_random_task,
            job_id='5F9914AB-2CC1-4A57-9A67-8586ADC2D8B6',
            kwargs={
                'message': {'id': '5F9914AB-2CC1-4A57-9A67-8586ADC2D8B6'},
                'topic_name': 'test',
                'subscription_name': 'sub-test-djangomoduletest',
                'subject': 'MockedTask',
            },
        )
        worker = SimpleWorker([queue], connection=queue.connection, exception_handlers=[on_failure])
        worker.work(burst=True)

        change_url = reverse('admin:metroid_failedmessage_changelist')
        data = {'action': 'retry', '_selected_action': [1]}
        response = client.post(change_url, data, follow=True)

        # Run the retry task
        worker.work(burst=True)

        assert response.status_code == 200
        assert len([x.message for x in caplog.records if x.message == 'Attempting to retry id 1']) == 1
    assert FailedMessage.objects.get(id=2)  # Prev message should fail
    with pytest.raises(FailedMessage.DoesNotExist):
        FailedMessage.objects.get(id=1)  # message we created above should be deleted
