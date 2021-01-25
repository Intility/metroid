# Metro for Django

This app is intended to streamline usage of Metro for all Django users.

## General
This app is intended to run as a standalone service together with Celery.

If this is not your use case, please look at the
[Metro Python Samples](***REMOVED***)
for smaller implementations.


### Overview

The `python manage.py metro` app is fully asynchronous, and has no blocking code.

It works by:
1. Going through all your configured subscriptions and start a new async connection with each one of them
2. Metro sends messages on the subscriptions
3. This app filters out messages matching subjects you have defined, and queues a celery task to execute
   the function as specified for that subject
4. The app marks the task as deferred
5. Your function must mark the message as complete when it is completed.

![overview](./readme_image.svg)

### API

#### Settings
Example settings:
```python
from demoproj.demoapp.services import my_func
METRO = {
    'subscriptions': [
        {
            'topic_name': 'metro-demo',
            'subscription_name': 'sub-metrodemo-metrodemoerfett',
            'connection_string': config('CONNECTION_STRING_METRO_DEMO', None),
            'handlers': [{'subject': 'MetroDemo/Type/GeekJokes', 'handler_function': my_func}],
        },
    ]
}
```

#### Callables

Your functions will be called with keyword arguments for
`message`, `topic_name`, `subscription_name` and `sequence_number`. You function should in other words
look something like this:

```python
def my_func(*, message: dict, topic_name: str, subscription_name: str, sequence_number: int) -> None:
```

#### Marking a message as completed
All your callables that handle messages should mark the message as completed, so that it can be removed from the
`deferred` queue in Metro.
You can do this by calling the `metro.complete.complete_deferred_message` function.

From a **sync** context, do this:

```python
from asgiref.sync import sync_to_async
sync_to_async(complete_deferred_message)(
    sequence_number=sequence_number, topic_name=topic_name, subscription_name=subscription_name
)
```

From an **async** context, do this:

```python
await complete_deferred_message(
    sequence_number=sequence_number, topic_name=topic_name, subscription_name=subscription_name
)
```



### TODO
* Implement APIs to GET all deferred messages
* Implement a way to retry a message based on a sequence ID
