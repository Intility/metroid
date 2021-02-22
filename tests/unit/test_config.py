from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

import pytest

from metroid.config import Settings, settings


def test_metro_is_not_in_settings_exception():
    """
    Deletes Metro from settings, and checks if the correct exception is thrown.
    """

    with pytest.raises(ImproperlyConfigured) as e:
        delattr(django_settings, 'METROID')
        Settings()

    assert str(e.value) == '`METROID` settings must be defined in settings.py'


def test_get_x_metro_key_raises_correctly():
    """
    Tests if the method get_x_metro_key raises an exception when no key is found.
    """
    with override_settings(METROID={'subscriptions': [], 'publish_settings': []}):
        mock_settings = Settings()
        with pytest.raises(ImproperlyConfigured):
            mock_settings.get_x_metro_key(
                topic_name='test2',
            )


def test_publish_topic_name_settings_not_string():
    """
    Tests if the method get_x_metro_key raises an exception when no key is found.
    """
    with override_settings(METROID={'publish_settings': [{'topic_name': 123}]}):
        with pytest.raises(ImproperlyConfigured) as e:
            mock_settings = Settings()
            mock_settings.validate()
        assert str(e.value) == 'Topic name must be a string'


def test_publish_metro_key_settings_not_string():
    """
    Tests if the method get_x_metro_key raises an exception when no key is found.
    """
    with override_settings(METROID={'publish_settings': [{'topic_name': 'topicName', 'x_metro_key': 123}]}):
        with pytest.raises(ImproperlyConfigured) as e:
            mock_settings = Settings()
            mock_settings.validate()
        assert str(e.value) == 'x_metro_key must be a string'


def test_get_x_metro_key_returns_when_found():
    with override_settings(
        METROID={'subscriptions': [], 'publish_settings': [{'topic_name': 'test2', 'x_metro_key': 'asdf'}]}
    ):
        mock_settings = Settings()
        metro_key = mock_settings.get_x_metro_key(topic_name='test2')
        assert metro_key == 'asdf'


def test_publish_settings_is_not_list_exception():
    """
    Provides subscriptions as a string instead of a list, and checks if the correct exception is thrown.
    """
    with override_settings(METROID={'publish_settings': 'i am string'}):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == 'Publish settings must be a list'


def test_subscriptions_is_not_list_exception():
    """
    Provides subscriptions as a string instead of a list, and checks if the correct exception is thrown.
    """
    with override_settings(METROID={'subscriptions': 'i am string'}):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()

        assert str(e.value) == 'Subscriptions must be a list'


def test_topic_name_is_not_str_exception():
    """
    Provides topic_name as an integer instead of a string, and checks if the correct exception is thrown.
    """
    topic_name_value = 123
    with override_settings(
        METROID={
            'subscriptions': [
                {
                    'topic_name': topic_name_value,
                    'subscription_name': 'hello',
                    'handlers': [],
                    'connection_string': 'Endpoint=sb://...',
                }
            ]
        }
    ):
        with pytest.raises(ImproperlyConfigured) as e:
            invalid_settings = Settings()
            invalid_settings.validate()
        assert str(e.value) == f'Topic name {topic_name_value} must be a string'


def test_subscription_name_is_not_str_exception():
    """
    Provides subscription_name  as None instead of a string, and checks if the correct exception is thrown.
    """
    subscription_name = None
    with override_settings(
        METROID={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': subscription_name,
                    'handlers': [],
                    'connection_string': 'Endpoint=sb://...',
                }
            ]
        }
    ):
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
        METROID={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': connection_string,
                    'handlers': [],
                }
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
        METROID={
            'subscriptions': [
                {
                    'topic_name': 'test',
                    'subscription_name': 'coolest/sub/ever',
                    'connection_string': connection_string,
                    'handlers': [],
                }
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
        METROID={
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
        METROID={
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
        METROID={
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
    Provides handler_function in an invalid format, and checks if the correct exception is thrown.
    """
    topic_name = 'test'
    subject = 'test/banonza'
    handler_function = None
    with override_settings(
        METROID={
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
            invalid_settings._validate_import_strings()
        assert str(e.value) == f'Handler function:{handler_function} for {topic_name} must be a string'


def test_handler_function_is_not_dotted_path_exception():
    """
    Provides handler_function in an invalid dotted path format, and checks if the correct exception is thrown.
    """
    topic_name = 'test'
    subject = 'test/banonza'
    handler_function = 'testtesttest'
    with override_settings(
        METROID={
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
            invalid_settings._validate_import_strings()

        assert str(e.value) == f'Handler function:{handler_function} for {topic_name} is not a dotted function path'


def test_handler_function_module_not_found_exception():
    """
    Provides handler_function with a non-existing module, and checks if the correct exception is thrown.
    """
    topic_name = 'test'
    subject = 'test/banonza'
    handler_function = 'test.test.test'
    with override_settings(
        METROID={
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
            invalid_settings._validate_import_strings()

        assert str(e.value) == f'Handler function:{handler_function} for {topic_name} cannot find module'


def test_handler_function_method_not_found_exception():
    """
    Provides handler_function with a non-existing method, and checks if the correct exception is thrown.
    """
    topic_name = 'test'
    subject = 'test/banonza'
    handler_function = 'demoproj.tasks.notfound'
    with override_settings(
        METROID={
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
            invalid_settings._validate_import_strings()

        assert (
            str(e.value) == f'Handler function:{handler_function}'
            f' for {topic_name} cannot be imported. Verify that the dotted path points to a function'
        )


def test_no_exception_is_thrown():
    """
    Provides mock_subscriptions, which is in valid format and checks if no exception is thrown.
    """
    try:
        with override_settings(
            METROID={
                'subscriptions': [
                    {
                        'topic_name': 'test',
                        'subscription_name': 'sub-test-djangomoduletest',
                        'connection_string': 'Endpoint=sb://cool',
                        'handlers': [
                            {
                                'subject': 'Test/Django/Module',
                                'handler_function': 'demoproj.tasks.a_random_task',
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
