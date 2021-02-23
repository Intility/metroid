import json

from django.utils import timezone

import pytest

from metroid.publish import publish_event


@pytest.fixture
def mock_response_ok(mocker):
    return_mock = mocker.Mock()
    mocker.patch('metroid.publish.requests', return_mock)
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
