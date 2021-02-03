from typing import Callable, Optional, Union

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from metro.typing import Subscription, Subscriptions


class Settings:
    """
    Subscriptions should be in this format:
    TODO: Implement connection string generator as Thomas ***REMOVED*** did
     Insp: ***REMOVED***

    As confirmed in Metro on slack, there will be 1 key per topic. This has been a deciding factor in
    how settings are implemented.
    ***REMOVED***

    METRO = {
        'subscriptions': {
            [
                {
                    'topic_name': '***REMOVED***',
                    'subscription_name': 'sub-***REMOVED***--helloworld',
                    'connection_string': 'Endpoint=sb://...',
                    'handlers': [
                        {
                            'subject': 'MetroDemo/Type/GeekJokes',
                            'handler_function': function_to_call,
                        },
                        {
                            'subject': 'MetroDemo/Type/DadJokes',
                            'handler_function': another_func_to_call
                        }
                    ]
                },
            ]
    }
    """

    def __init__(self) -> None:
        if hasattr(django_settings, 'METRO'):
            # self.settings: dict[str, list[dict[str, Union[str, list[dict[str, Callable]]]]]] = django_settings.METRO
            self.settings: Subscriptions = django_settings.METRO
        else:
            raise ImproperlyConfigured('`METRO` settings must be defined in settings.py')

    @property
    def subscriptions(self) -> list[Subscription]:
        """
        Returns all subscriptions
        """
        return self.settings['subscriptions']

    def get_subscription_string(self, *, topic_name: str, subscription_name: str) -> Union[str, None]:
        """
        Fetches the subscription string based on topic and subscription name
        """
        for subscription in self.subscriptions:
            if (
                subscription.get('topic_name') == topic_name
                and subscription.get('subscription_name') == subscription_name
            ):
                # TODO: Fix mypy
                return subscription['connection_string']  # type: ignore
        return None

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
                        return handler.get('handler_function')
        return None

    def validate(self) -> None:
        """
        Validates all settings
        TODO: Harden it
        """
        if not isinstance(self.subscriptions, list):
            raise ImproperlyConfigured('Subscriptions must be a :qlist')
        for subscription in self.subscriptions:
            topic_name = subscription.get('topic_name', None)
            subscription_name = subscription.get('subscription_name', None)
            connection_string = subscription.get('connection_string', None)
            handlers = subscription.get('handlers', None)
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
            if not isinstance(handlers, dict):
                raise ImproperlyConfigured(f'Handler function {handlers} must be a dict')
            for handler in handlers:
                subject = handler.get('subject')
                handler_function = handler.get('handler_function')
                if not isinstance(subject, str):
                    raise ImproperlyConfigured(f'Handler subject {subject} for {topic_name} must be a string')
                if not isinstance(handler_function, Callable):
                    raise ImproperlyConfigured(
                        f'Handler function {handler_function} for {topic_name} must be a Callable'
                    )


settings = Settings()
