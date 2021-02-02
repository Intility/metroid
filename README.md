[![Py](https://img.shields.io/badge/python-v3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-3.1.1+%20-blue.svg)](https://djangoproject.com)
[![Celery](https://img.shields.io/badge/celery-5.0.0+%20-blue.svg)](https://docs.celeryproject.org/en/stable/)
[![Django-GUID](https://img.shields.io/badge/django--guid-3.2.0+-blue.svg)](https://github.com/snok/django-guid/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# Metro for Django

This app is intended to streamline integration with Metro for all Django users by:

* Asynchronous handling of subscriptions and messages with one command
* Sends all tasks to Celery workers, based on your `settings.py`
* Retry failed tasks through your admin dashboard when using the `MetroTask` base

## Overview
* `python` >= 3.9 - We're using the newest versions of type annotations
* `django` >= 3.1.1 - For `asgiref` and `django-guid` dependencies
* `celery` >= 5.0.0 - Might work on previous versions, but not supported
* `django-guid` >= 3.2.0 - Storing correlation IDs in the database, making debugging easy

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
   3.1. If no task is found for that subject, the message is marked as complete
4. The message is marked as complete after the Celery task has successfully been queued
5. If the task is failed, an entry is automatically created in your database
6. All failed tasks can be retried manually through the admin dashboard


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
The handlers subject can be a reggex pattern or a string. If a string with characters that need to be escaped is detected by re.compile, they will be escaped. The pattern matching for the subject works in this scenarios:

`'subject': 'MetroDemo/Type/GeekJokes'` would match all messages with subject:`'MetroDemo/Type/GeekJokes' `

`'subject': 'MetroDemo/Type/GeekJokes[cool]'` would match all messages with subject:`'MetroDemo/Type/GeekJokes[cool]'`

`'subject': '^MetroDemo/Type/.*$'` would match all messages with subjects that start with: `MetroDemo/Type/`

`'subject': '^MetroDemo/Type/.*$123456'` would match all messages with subjects that start with: `MetroDemo/Type/`. It will not match strings that have number after '$' as it is a valid reggex character.




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
1. Ensure you have redis running:
```bash
docker-compose up
```
2. Run migrations
```bash
python manage.py migrate
```
3. Create an admin account
```bash
python manage.py createsuperuser
```
4. Start a worker:
```python
celery -A demoproj worker -l info
```
5. Run the subscriber:
```python
python manage.py metro
```
6. Send messages to Metro. Example code can be found in [`demoproj/demoapp/services.py`](demoproj/demoapp/services.py)
7. Run the webserver:
```python
python manage.py runserver 8000
```
8. See failed messages under `http://localhost:8080/admin`

To contribute, please see [`CONTRIBUTING.md`](CONTRIBUTING.md)

### TODO
* Tests
* Support regex patterns
