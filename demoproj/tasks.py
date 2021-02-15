from demoproj.celery import app
from metro.celery import MetroTask


@app.task(base=MetroTask, name='demoproj.tasks.a_random_task')
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


@app.task(base=MetroTask, name='demoproj.tasks.my_task')
def my_task(**kwargs) -> None:
    """
    Function used for testing, returns nothing.
    """
    return None
