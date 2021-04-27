from typing import Callable, List, Literal, TypedDict


class Handler(TypedDict):
    subject: str
    regex: bool
    handler_function: Callable


class Subscription(TypedDict):
    topic_name: str
    subscription_name: str
    connection_string: str
    handlers: List[Handler]


class TopicPublishSettings(TypedDict):
    topic_name: str
    x_metro_key: str


class MetroidSettings(TypedDict):
    subscriptions: List[Subscription]
    publish_settings: List[TopicPublishSettings]
    worker_type: Literal['rq', 'celery']
