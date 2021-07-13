<h1 align="center">
  <img src=".github/images/intility.png" width="124px"/><br/>
  Metroid
</h1>

<p align="center">
    <em>Subscribe, act, publish.</em>
</p>
<p align="center">
    <a href="https://python.org">
        <img src="https://img.shields.io/badge/python-v3.9+-blue.svg" alt="Python version">
    </a>
    <a href="https://djangoproject.com">
        <img src="https://img.shields.io/badge/django-3.1.1+%20-blue.svg" alt="Django version">
    </a>
    <a href="https://docs.celeryproject.org/en/stable/">
        <img src="https://img.shields.io/badge/celery-5.0.0+%20-blue.svg" alt="Celery version">
    </a>
    <a href="https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus">
        <img src="https://img.shields.io/badge/azure--servicebus-7.0.1+%20-blue.svg" alt="ServiceBus version">
    </a>
    <a href="https://github.com/snok/django-guid/">
        <img src="https://img.shields.io/badge/django--guid-3.2.0+-blue.svg" alt="Django GUID version">
    </a>
</p>
<p align="center">
    <a href="https://codecov.io/gh/intility/metroid">
        <img src="https://codecov.io/gh/intility/metroid/branch/main/graph/badge.svg" alt="Codecov">
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="Pre-commit">
    </a>
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
    </a>
    <a href="http://mypy-lang.org">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="mypy">
    </a>
    <a href="https://pycqa.github.io/isort/">
        <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="isort">
    </a>
</p>


# Metroid - Metro for Django

This app is intended to streamline integration with Metro for all Django+Celery users by:

* Asynchronous handling of subscriptions and messages with one command
* Execute Celery tasks based on message topics, defined in `settings.py`
* Retry failed tasks through your admin dashboard when using the `MetroidTask` base

## Overview
* `python` >= 3.8
* `django` >= 3.1.1 - For `asgiref`, settings
* `django-guid` >= 3.2.0 - Storing correlation IDs for failed tasks in the database, making debugging easy
* Choose one:
   * `celery` >= 5.0.0 - Execute tasks based on a subject
   * `rq` >= 2.4.1 - Execute tasks based on a subject

### Implementation

The `python manage.py metroid` app is fully asynchronous, and has no blocking code. It utilizes `Celery` to execute tasks.

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

1. Create a `METROID` key in `settings.py` with all your subscriptions and handlers.
Example settings:
```python
METROID = {
    'subscriptions': [
        {
            'topic_name': 'metro-demo',
            'subscription_name': 'sub-metrodemo-metrodemoerfett',
            'connection_string': config('CONNECTION_STRING_METRO_DEMO', None),
            'handlers': [
               {
                  'subject': 'MetroDemo/Type/GeekJokes',
                  'regex': False,
                  'handler_function': 'demoproj.demoapp.services.my_func'
                }
            ],
        },
    ],
   'worker_type': 'celery', # default
}
```

The `handler_function` is defined by providing the full dotted path as a string. For example,`from demoproj.demoapp.services import my_func` is provided as `'demoproj.demoapp.services.my_func'`.

The handlers subject can be a regular expression or a string. If a regular expression is provided, the variable regex must be set to True. Example:
 ```python
'handlers': [{'subject': r'^MetroDemo/Type/.*$','regex':True,'handler_function': my_func}],
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

##### Celery
```python
@app.task(base=MetroidTask)
def my_func(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
```

##### rq
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
python manage.py metroid
```
6. Send messages to Metro. Example code can be found in [`demoproj/demoapp/services.py`](demoproj/demoapp/services.py)
7. Run the webserver:
```python
python manage.py runserver 8000
```
8. See failed messages under `http://localhost:8080/admin`

To contribute, please see [`CONTRIBUTING.md`](CONTRIBUTING.md)
