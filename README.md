[![Py](https://img.shields.io/badge/Python-v3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-3.1.1+%20-blue.svg)](https://djangoproject.com)
[![Celery](https://img.shields.io/badge/Celery-5.0.0+%20-blue.svg)](https://docs.celeryproject.org/en/stable/)
[![Django-GUID](https://img.shields.io/badge/Django%20GUID-3.2.0+-blue.svg)](https://github.com/snok/django-guid/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# Metro for Django

This app is intended to streamline integration with Metro for all Django users by:

* Asynchronous handling of subscriptions and messages with one command
* Sends all tasks to Celery workers, based on your `settings.py`
* Retry failed tasks through your admin dashboard when using the `MetroTask` base

## Overview
* `Python` >= 3.9 - We're using the newest versions of type annotations
* `Celery` >= 5.0.0 - Might work on previous versions, but not supported
* `Django-GUID` >= 3.2.0 - Storing correlation IDs in the database, making debugging easy

If you're not running Celery or have another use case you can find pure Python examples in both sync and async versions
in the [Metro Python Samples](***REMOVED***)
repository.


### Implementation

The `python manage.py metro` app is fully asynchronous, and has no blocking code. It utilizes `Celery` to execute tasks.

It works by:
1. Going through all your configured subscriptions and start a new async connection for each one of them
2. Metro sends messages on the subscriptions
3. This app filters out messages matching subjects you have defined, and queues a celery task to execute
   the function as specified for that subject
4. If the task is failed, an entry is automatically created in your database
5. All failed tasks can be retried manually through the admin dashboard


### Configure and install this package


> **_Note_**
> For a complete example, have a look in `demoproj/settings.py`.

1. Create a `METRO` key in `settings.py` with all your subscriptions and handlers.
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

2. Configure `Django-GUID`  by adding the app to your installed apps, to your middlewares and configuring logging
as described [here](https://github.com/snok/django-guid#configuration).
Make sure you enable the [`CeleryIntegration`](https://django-guid.readthedocs.io/en/latest/integrations.html#celery):
```python
from django_guid.integrations import CeleryIntegration

DJANGO_GUID = {
    'INTEGRATIONS': [
        CeleryIntegration(
            use_django_logging=True,
            log_parent=True,
        )
    ],
}
```


#### Creating your own handler functions

Your functions will be called with keyword arguments for


`message`, `topic_name`, `subscription_name` and `subject`. You function should in other words
look something like this:

```python
def my_func(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
```


### Running the project
Ensure you have redis running:
```bash
docker-compose up
```
Start a worker:
```python
celery -A demoproj worker -l info
```
Run the subscriber:
```python
python manage.py metro
```

### TODO
* Tests
* Support regex patterns
