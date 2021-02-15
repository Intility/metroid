from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

import pytest
from metro.config import Settings, settings


def test_metro_is_not_in_settings_exception():
    """
    Deletes Metro from settings, and checks if the correct exception is thrown.
    """

    with pytest.raises(ImproperlyConfigured) as e:
        delattr(django_settings, 'METRO')
        Settings()

    assert str(e.value) == '`METRO` settings must be defined in settings.py'


def test_get_subscription_string_returns_none():
    """
    Tests if the method get_subscription_string returns None, when no matching topic_name and subscription_name is
    provided.
    """
    topic_name = 'test'
    subscription_name = 'coolest/sub/ever'
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': topic_name,
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': 'Endpoint=sb://cool',
                    'handlers': [{'subject': 'test/banonza', 'handler_function': 'i am a function'}],
                }
            ]
        }
    ):
        mock_settings = Settings()
        get_subscription = mock_settings.get_subscription_string(
            topic_name='test2', subscription_name=subscription_name
        )
        assert get_subscription is None


def test_get_subscription_string_returns_correct_connection_string():
    """
    Tests if the method get_subscription_string returns the correct connection_string, when a matching topic_name
    and subscription_name is provided.
    """
    topic_name = 'test'
    subscription_name = 'coolest/sub/ever'
    connection_string = 'Endpoint=sb://cool'
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': topic_name,
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': connection_string,
                    'handlers': [{'subject': 'test/banonza', 'handler_function': 'i am a function'}],
                },
                {
                    'topic_name': 'test2',
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': 'Endpoint=sb://notsocool',
                    'handlers': [{'subject': 'test/banonza', 'handler_function': 'i am a function'}],
                },
            ]
        }
    ):
        mock_settings = Settings()
        get_subscription = mock_settings.get_subscription_string(
            topic_name=topic_name, subscription_name=subscription_name
        )
        assert get_subscription is connection_string


def test_subscriptions_is_not_list_exception():
    """
    Provides subscriptions as a string instead of a list, and checks if the correct exception is thrown.
    """
    with override_settings(METRO={'subscriptions': 'i am string'}):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == 'Subscriptions must be a list'


def test_topic_name_is_not_str_exception():
    """
    Provides topic_name as an integer instead of a string, and checks if the correct exception is thrown.
    """
    topic_name_value = 123
    with override_settings(METRO={'subscriptions': [{'topic_name': topic_name_value}]}):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Topic name {topic_name_value} must be a string'


def test_subscription_name_is_not_str_exception():
    """
    Provides subscription_name  as None instead of a string, and checks if the correct exception is thrown.
    """
    subscription_name = None
    with override_settings(METRO={'subscriptions': [{'topic_name': 'test', 'subscription_name': subscription_name}]}):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Subscription name {subscription_name} must be a string'


def test_connection_string_is_not_str_exception():
    """
    Provides connection_string  as bool instead of a string, and checks if the correct exception is thrown.
    """
    connection_string = bool
    with override_settings(
        METRO={
            'subscriptions': [
                {'topic_name': 'test', 'subscription_name': 'coolest/sub/ever', 'connection_string': connection_string}
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Connection string {connection_string} must be a string'


def test_connection_string_does_not_start_with_endpoint():
    """
    Provides connection_string  in an invalid format, and checks if the correct exception is thrown.
    """
    connection_string = 'Where is my endpoint!?'
    with override_settings(
        METRO={
            'subscriptions': [
                {'topic_name': 'test', 'subscription_name': 'coolest/sub/ever', 'connection_string': connection_string}
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Invalid connection string: {connection_string}. Must start with Endpoint=sb://'


def test_handlers_is_not_list_exception():
    """
    Provides handlers as a dict, and checks if the correct exception is thrown.
    """
    handlers = {}
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': 'Endpoint=sb://cool',
                    'handlers': handlers,
                }
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Handler function {handlers} must be a list'


def test_handler_in_handlers_is_not_dict_exception():
    """
    Provides the handler_function in an invalid format, and checks if the correct exception is thrown.
    """
    handler = 'subject'
    handlers = [handler]
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': 'Endpoint=sb://cool',
                    'handlers': ['subject'],
                }
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'{handlers} must contain dict values, got: {handler}'


def test_subject_is_not_str_exception():
    """
    Provides connection_string  in an invalid format, and checks if the correct exception is thrown.
    """
    topic_name = 'test'
    subject = 123
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': topic_name,
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': 'Endpoint=sb://cool',
                    'handlers': [{'subject': subject}],
                }
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Handler subject {subject} for {topic_name} must be a string'


def test_handler_function_is_not_str_exception():
    """
    Provides connection_string in an invalid format, and checks if the correct exception is thrown.
    """
    topic_name = 'test'
    subject = 'test/banonza'
    handler_function = test_subject_is_not_str_exception()
    with override_settings(
        METRO={
            'subscriptions': [
                {
                    'topic_name': topic_name,
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': 'Endpoint=sb://cool',
                    'handlers': [{'subject': subject, 'handler_function': handler_function}],
                }
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == f'Handler function {handler_function} for {topic_name} must be a Callable'


def test_no_exception_is_thrown():
    """
    Provides mock_subscriptions, which is in valid format and checks if no exception is thrown.
    """
    try:
        with override_settings(
            METRO={
                'subscriptions': [
                    {
                        'topic_name': 'test',
                        'subscription_name': 'sub-test-djangomoduletest',
                        'connection_string': 'Endpoint=sb://cool',
                        'handlers': [
                            {
                                'subject': 'Test/Django/Module',
                                'handler_function': 'tests.functional.test_celery.a_random_task',
                            },
                        ],
                    }
                ]
            }
        ):
            mock_settings = Settings()
            mock_settings.validate()
    except Exception as e:
        pytest.fail('Settings validation should not throw an exception with correct mock data')
