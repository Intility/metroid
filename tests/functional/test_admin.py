from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse

import pytest
from metro.config import Settings
from metro.models import FailedMessage
from tests.functional.test_celery import a_random_task


@pytest.fixture
def create_and_sign_in_user(client):
    user = User.objects.create_superuser('testuser', 'test@test.com', 'testpw')
    client.login(username='testuser', password='testpw')
    return


@pytest.fixture()
def mock_subscriptions_admin(monkeypatch):
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'sub-test-djangomoduletest',
                    'connection_string': 'my long connection string',
                    'handlers': [
                        {'subject': 'MockedTask', 'handler_function': a_random_task},
                        {'subject': 'ErrorTask', 'handler_function': lambda x: None},
                    ],
                },
            ]
        }
    ):
        settings = Settings()
        monkeypatch.setattr('metro.admin.settings', settings)


@pytest.mark.django_db
def test_admin_action_no_handler(client, caplog, create_and_sign_in_user):
    content = FailedMessage.objects.create(
        topic_name='test_topic',
        subscription_name='test_sub',
        subject='test subj',
        message='my message',
        exception_str='exc',
        traceback='long trace',
        correlation_id='',
    )
    change_url = reverse('admin:metro_failedmessage_changelist')
    data = {'action': 'retry', '_selected_action': [content.id]}
    x = client.post(change_url, data, follow=True)
    assert x.status_code == 200
    assert len([x.message for x in caplog.records if x.message == 'No handler found for 1']) == 1


@pytest.mark.django_db
def test_admin_action_handler_found(client, caplog, create_and_sign_in_user, mock_subscriptions_admin):
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        content = FailedMessage.objects.create(
            topic_name='test',
            subscription_name='sub-test-djangomoduletest',
            subject='MockedTask',
            message='my message',
            exception_str='exc',
            traceback='long trace',
            correlation_id='',
        )

        change_url = reverse('admin:metro_failedmessage_changelist')
        data = {'action': 'retry', '_selected_action': [content.id]}
        x = client.post(change_url, data, follow=True)
        assert x.status_code == 200
        assert len([x.message for x in caplog.records if x.message == 'Attempting to retry id 1']) == 1
    assert FailedMessage.objects.get(id=2)  # Prev message should fail
    with pytest.raises(FailedMessage.DoesNotExist):
        FailedMessage.objects.get(id=1)  # message we created above should be deleted


@pytest.mark.django_db
def test_admin_action_failed_retry(client, caplog, create_and_sign_in_user, mock_subscriptions_admin):
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        content = FailedMessage.objects.create(
            topic_name='test',
            subscription_name='sub-test-djangomoduletest',
            subject='ErrorTask',
            message='my message',
            exception_str='exc',
            traceback='long trace',
            correlation_id='',
        )
        change_url = reverse('admin:metro_failedmessage_changelist')
        data = {'action': 'retry', '_selected_action': [content.id]}
        x = client.post(change_url, data, follow=True)
        assert x.status_code == 200
        assert len([x.message for x in caplog.records if x.message == 'Attempting to retry id 1']) == 1
        assert (
            len(
                [
                    x.message
                    for x in caplog.records
                    if x.message
                    == "Unable to retry Metro message. Error: 'function' object has no attribute 'apply_async'"
                ]
            )
            == 1
        )
