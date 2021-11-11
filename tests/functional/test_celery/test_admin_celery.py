from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

import pytest
from urllib3.exceptions import HTTPError

from metroid.config import Settings
from metroid.models import FailedMessage, FailedPublishMessage


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
        }
    ):
        settings = Settings()
        monkeypatch.setattr('metroid.admin.settings', settings)


@pytest.fixture
def mock_republish_error(mocker):
    return_mock = mocker.Mock()
    return_mock.post.side_effect = HTTPError(mocker.Mock(status_code=500))

    mocker.patch('metroid.admin.requests', return_mock)
    return return_mock


@pytest.mark.django_db
def test_admin_action_no_handler_celery(client, caplog, create_and_sign_in_user):
    content = FailedMessage.objects.create(
        topic_name='test_topic',
        subscription_name='test_sub',
        subject='test subj',
        message='my message',
        exception_str='exc',
        traceback='long trace',
        correlation_id='',
    )
    change_url = reverse('admin:metroid_failedmessage_changelist')
    data = {'action': 'retry', '_selected_action': [content.id]}
    response = client.post(change_url, data, follow=True)
    assert response.status_code == 200
    assert len([x.message for x in caplog.records if x.message == 'No handler found for 1']) == 1


@pytest.mark.django_db
def test_admin_action_handler_found_celery(client, caplog, create_and_sign_in_user, mock_subscriptions_admin):
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
        change_url = reverse('admin:metroid_failedmessage_changelist')
        data = {'action': 'retry', '_selected_action': [content.id]}
        response = client.post(change_url, data, follow=True)
        assert response.status_code == 200
        assert len([x.message for x in caplog.records if x.message == 'Attempting to retry id 1']) == 1
    assert FailedMessage.objects.get(id=2)  # Prev message should fail
    with pytest.raises(FailedMessage.DoesNotExist):
        FailedMessage.objects.get(id=1)  # message we created above should be deleted


@pytest.mark.django_db
def test_admin_action_failed_retry_celery(client, caplog, create_and_sign_in_user, mock_subscriptions_admin):
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
        change_url = reverse('admin:metroid_failedmessage_changelist')
        data = {'action': 'retry', '_selected_action': [content.id]}
        response = client.post(change_url, data, follow=True)
        assert response.status_code == 200
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


@pytest.mark.django_db
def test_admin_action_retry_publish(client, caplog, create_and_sign_in_user, requests_mock):
    now = timezone.now().isoformat()
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        content = FailedPublishMessage.objects.create(
            event_type='Intility.MyTopic',
            event_time=now,
            data_version='1.0',
            data={'hello': 'world'},
            subject='my/test/subject',
            topic_name='test123',
        )

        assert FailedPublishMessage.objects.get(id=1)
        requests_mock.post('https://api.intility.no/metro/test123', status_code=200)
        change_url = reverse('admin:metroid_failedpublishmessage_changelist')
        data = {'action': 'retry_publish', '_selected_action': [content.id]}
        response = client.post(change_url, data, follow=True)

        assert response.status_code == 200
        with pytest.raises(FailedPublishMessage.DoesNotExist):
            FailedPublishMessage.objects.get(id=1)  # message we created above should be deleted


@pytest.mark.django_db
def test_admin_action_retry_publish_error(client, caplog, create_and_sign_in_user, requests_mock):
    now = timezone.now().isoformat()
    with override_settings(CELERY_TASK_ALWAYS_EAGER=True):
        content = FailedPublishMessage.objects.create(
            event_type='Intility.MyTopic',
            event_time=now,
            data_version='1.0',
            data={'hello': 'world'},
            subject='my/test/subject',
            topic_name='test123',
        )

        assert FailedPublishMessage.objects.get(id=1)
        requests_mock.post('https://api.intility.no/metro/test123', status_code=500)
        change_url = reverse('admin:metroid_failedpublishmessage_changelist')
        data = {'action': 'retry_publish', '_selected_action': [content.id]}
        response = client.post(change_url, data, follow=True)
        assert response.status_code == 200
        assert FailedPublishMessage.objects.get(id=1)  # message we created above should not be deleted
