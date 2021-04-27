from demoproj.celery import app

from metroid.celery import MetroidTask


@app.task(base=MetroidTask)
def a_random_task(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> Exception:
    """
    Mocked function for tests. Matches on the subject 'MockedTask'.
    """
    raise ValueError('My mocked error :)')


def error_task(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
    """
    Mocked function for tests, is to be ran on the subject 'ErrorTask'. This function does nothing, and is meant to
    tests tasks without the Celery annotation.
    """
    lambda x: None


@app.task(base=MetroidTask)
def my_task(**kwargs) -> None:
    """
    Function used for testing, returns nothing.
    """
    return None


@app.task(base=MetroidTask)
def example_celery_task(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
    """
    Celery Example Task
    """
    print('Do Something')  # noqa: T001


def example_rq_task(*, message: dict, topic_name: str, subscription_name: str, subject: str) -> None:
    """
    RQ Example Task
    """
    print('Do Something')  # noqa: T001
