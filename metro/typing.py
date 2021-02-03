from typing import Callable, TypedDict


class Handler(TypedDict):
    subject: str
    regex: bool
    handler_function: Callable


class Subscription(TypedDict):
    topic_name: str
    subscription_name: str
    connection_string: str
    handlers: list[Handler]


class Subscriptions(TypedDict):
    subscriptions: list[Subscription]
