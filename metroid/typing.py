from collections.abc import Callable
from typing import Literal, TypedDict


class Handler(TypedDict):
    subject: str
    regex: bool
    handler_function: Callable


class Subscription(TypedDict):
    topic_name: str
    subscription_name: str
    connection_string: str
    handlers: list[Handler]


class TopicPublishSettings(TypedDict):
    topic_name: str
    x_metro_key: str


class MetroidSettings(TypedDict):
    subscriptions: list[Subscription]
    publish_settings: list[TopicPublishSettings]
    worker_type: Literal['rq', 'celery']
