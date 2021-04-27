import logging
from typing import Callable, List, Optional, Union

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from metroid.typing import MetroidSettings, Subscription, TopicPublishSettings

logger = logging.getLogger('metroid')


class Settings:
    """
    Subscriptions should be in this format:

    METROID = {
        'subscriptions': [
            {
                'topic_name': 'test',
                'subscription_name': 'sub-test-helloworld',
                'connection_string': 'Endpoint=sb://...',
                'handlers': [
                    {
                        'subject': '^MetroDemo/Type/.*',
                        'regex': True,
                        'handler_function': function_to_call,
                    },
                    {
                        'subject': 'MetroDemo/Type/DadJokes.Created',
                        'regex': False,
                        'handler_function': another_func_to_call
                    }
                ],
            },
        ],
        'publish_settings': [
            {
                'topic_name': 'test',
                'x_metro_key': 'my-metro-key',
            },
            {
                'topic_name': 'another_topic',
                'x_metro_key': 'my-other-metro-key',
            },
        ],
        'worker_type': 'celery' # default
    }
    """

    def __init__(self) -> None:
        if hasattr(django_settings, 'METROID'):
            self.settings: MetroidSettings = django_settings.METROID
        else:
            raise ImproperlyConfigured('`METROID` settings must be defined in settings.py')

    @property
    def subscriptions(self) -> List[Subscription]:
        """
        Returns all subscriptions
        """
        return self.settings.get('subscriptions', [])

    @property
    def publish_settings(self) -> List[TopicPublishSettings]:
        """
        Returns all publish to metro settings
        """
        return self.settings.get('publish_settings', [])

    @property
    def worker_type(self) -> str:
        """
        Returns the worker type.
        """
        return self.settings.get('worker_type', 'celery')

    def get_x_metro_key(self, *, topic_name: str) -> Union[str, None]:
        """
        Fetches the x-metro-key based on topic
        """
        for topic in self.publish_settings:
            if topic['topic_name'] == topic_name:
                return topic['x_metro_key']
        logger.critical('Unable to find a x-metro-key for %s', topic_name)
        raise ImproperlyConfigured(f'No x-metro-key found for {topic_name}')

    def get_handler_function(self, *, topic_name: str, subscription_name: str, subject: str) -> Optional[Callable]:
        """
        Intended to be used by retry-log.
        It finds the handler function based on information we have stored in the database.
        """
        for subscription in self.subscriptions:
            if (
                subscription.get('topic_name') == topic_name
                and subscription.get('subscription_name') == subscription_name
            ):
                for handler in subscription['handlers']:
                    if handler.get('subject') == subject:
                        return import_string(handler.get('handler_function'))
        return None

    def _validate_import_strings(self) -> None:
        """
        Validates the handler_function string for handlers specified in the settings.
        """
        for subscription in self.subscriptions:
            topic_name = subscription.get('topic_name')
            handlers = subscription.get('handlers', [])
            for handler in handlers:
                handler_function = handler['handler_function']
                if not isinstance(handler_function, str):
                    raise ImproperlyConfigured(f'Handler function:{handler_function} for {topic_name} must be a string')

                try:
                    import_string(handler_function)
                except ModuleNotFoundError:
                    raise ImproperlyConfigured(
                        f'Handler function:{handler_function} for {topic_name} cannot find module'
                    )
                except ImportError as error:
                    if f"{handler_function} doesn't look like a module path" in str(error):
                        raise ImproperlyConfigured(
                            f'Handler function:{handler_function} for {topic_name} is not a dotted function path'
                        )
                    else:
                        raise ImproperlyConfigured(
                            f'Handler function:{handler_function} '
                            f'for {topic_name} cannot be imported. Verify that the dotted path points to a function'
                        )

    def validate(self) -> None:
        """
        Validates all settings
        """
        if self.worker_type == 'celery':
            try:
                import celery  # noqa: F401
            except ModuleNotFoundError:
                raise ImproperlyConfigured(
                    'The package `celery` is required when using `celery` as worker type. '
                    'Please run `pip install celery` if you with to use celery as the workers.'
                )
        elif self.worker_type == 'rq':
            try:
                import django_rq  # noqa: F401
            except ModuleNotFoundError:
                raise ImproperlyConfigured(
                    'The package `django-rq` is required when using `rq` as worker type. '
                    'Please run `pip install django-rq` if you with to use rq as the workers.'
                )
        else:
            raise ImproperlyConfigured("Worker type must be 'celery' or 'rq'")
        if not isinstance(self.subscriptions, list):
            raise ImproperlyConfigured('Subscriptions must be a list')
        if not isinstance(self.publish_settings, list):
            raise ImproperlyConfigured('Publish settings must be a list')
        for subscription in self.subscriptions:
            topic_name = subscription['topic_name']
            subscription_name = subscription['subscription_name']
            connection_string = subscription['connection_string']
            handlers = subscription['handlers']
            if not isinstance(topic_name, str):
                raise ImproperlyConfigured(f'Topic name {topic_name} must be a string')
            if not isinstance(subscription_name, str):
                raise ImproperlyConfigured(f'Subscription name {subscription_name} must be a string')
            if not isinstance(connection_string, str):
                raise ImproperlyConfigured(f'Connection string {connection_string} must be a string')
            if not connection_string.startswith('Endpoint=sb://'):
                raise ImproperlyConfigured(
                    f'Invalid connection string: {connection_string}. Must start with Endpoint=sb://'
                )
            if not isinstance(handlers, list):
                raise ImproperlyConfigured(f'Handler function {handlers} must be a list')
            for handler in handlers:
                if not isinstance(handler, dict):
                    raise ImproperlyConfigured(f'{handlers} must contain dict values, got: {handler}')
                subject = handler['subject']
                if not isinstance(subject, str):
                    raise ImproperlyConfigured(f'Handler subject {subject} for {topic_name} must be a string')

        for topic in self.publish_settings:
            if not isinstance(topic['topic_name'], str):
                raise ImproperlyConfigured('Topic name must be a string')
            if not isinstance(topic['x_metro_key'], str):
                raise ImproperlyConfigured('x_metro_key must be a string')
        self._validate_import_strings()


settings = Settings()
