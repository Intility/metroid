import json

from django.utils import timezone

import pytest
from urllib3.exceptions import HTTPError

from metroid.models import FailedPublishMessage
from metroid.publish import publish_event
from metroid.republish import retry_failed_published_events


@pytest.fixture
def mock_republish_error(mocker):
    return_mock = mocker.Mock()
    return_mock.post.side_effect = HTTPError(mocker.Mock(status_code=500))

    mocker.patch('metroid.republish.requests', return_mock)
    return return_mock


@pytest.fixture
def mock_republish_ok(mocker):
    return_mock = mocker.Mock()
    mocker.patch('metroid.republish.requests', return_mock)
    return return_mock


@pytest.mark.django_db
def test_failed_message_saved(mock_republish_error):
    now = timezone.now().isoformat()
    publish_event(
        topic_name='test123',
        event_type='Intility.MyTopic',
        data_version='1.0',
        data={'hello': 'world'},
        subject='my/test/subject',
        event_time=now,
    )

    assert len(FailedPublishMessage.objects.all()) == 1


@pytest.mark.django_db
def test_retry_failed_messages(mock_republish_ok):
    now = timezone.now().isoformat()
    FailedPublishMessage.objects.create(
        event_type='Intility.MyTopic',
        event_time=now,
        data_version='1.0',
        data={'hello': 'world'},
        subject='my/test/subject',
        topic_name='test123',
    )

    assert len(FailedPublishMessage.objects.all()) == 1
    retry_failed_published_events()

    mock_republish_ok.post.assert_called_with(
        url='https://api.intility.no/metro/test123',
        headers={'content-type': 'application/json', 'x-metro-key': 'my-metro-key'},
        data=json.dumps(
            {
                'eventType': 'Intility.MyTopic',
                'eventTime': now,
                'dataVersion': '1.0',
                'data': {'hello': 'world'},
                'subject': 'my/test/subject',
            }
        ),
    )
    assert len(FailedPublishMessage.objects.all()) == 0


@pytest.mark.django_db
def test_retry_failed_messages_fail(mock_republish_error):
    now = timezone.now().isoformat()
    FailedPublishMessage.objects.create(
        event_type='Intility.MyTopic',
        event_time=now,
        data_version='1.0',
        data={'hello': 'world'},
        subject='my/test/subject',
        topic_name='test123',
    )

    assert len(FailedPublishMessage.objects.all()) == 1
    retry_failed_published_events()
    assert len(FailedPublishMessage.objects.all()) == 1
