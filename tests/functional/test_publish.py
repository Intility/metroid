import json

from django.utils import timezone

import pytest
import requests

from metroid.models import FailedPublishMessage
from metroid.publish import publish_event
from metroid.republish import retry_failed_published_events


@pytest.fixture
def mock_response_ok(mocker):
    return_mock = mocker.Mock()
    mocker.patch('metroid.publish.requests', return_mock)
    return return_mock


@pytest.fixture
def mock_response_error(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'Error': 'Something went wrong'}
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

    return_mock = mocker.Mock()

    mocker.patch('metroid.publish.requests', return_mock)
    return_mock.return_value = mock_response

    return return_mock


def test_no_event_time_provided(mock_response_ok, freezer):
    now = timezone.now().isoformat()  # freezegun ensures time don't pass
    publish_event(
        topic_name='test123',
        event_type='Intility.MyTopic',
        data_version='1.0',
        data={'hello': 'world'},
        subject='my/test/subject',
    )

    mock_response_ok.post.assert_called_with(
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


def test_event_time_provided(mock_response_ok):
    now = timezone.now().isoformat()
    publish_event(
        topic_name='test123',
        event_type='Intility.MyTopic',
        data_version='1.0',
        data={'hello': 'world'},
        subject='my/test/subject',
        event_time=now,
    )
    mock_response_ok.post.assert_called_with(
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


@pytest.mark.django_db
def test_failed_message_saved(mock_response_error):
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
def test_retry_failed_messages(mock_response_ok):
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

    mock_response_ok.post.assert_called_with(
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
def test_retry_failed_messages_fail(mock_response_error):
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

    assert mock_response_error.raise_for_status
    assert len(FailedPublishMessage.objects.all()) == 1
