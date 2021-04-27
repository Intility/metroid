import logging
from typing import Any, Dict

from billiard.einfo import ExceptionInfo
from django_guid import get_guid

from celery import Task

logger = logging.getLogger('metroid')


class MetroidTask(Task):
    def on_failure(
        self, exc: Exception, task_id: str, args: tuple, kwargs: Dict[str, Any], einfo: ExceptionInfo
    ) -> None:
        """
        Custom error handler for Metro Celery tasks.
        This function is automatically run by the worker when the task fails.

        :param exc: The exception raised by the task.
        :param task_id: Unique ID of the failed task.
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed
        :param einfo: Exception information
        :return: The return value of this handler is ignored, so it should not return anything
        """
        # pass
        topic_name = kwargs.get('topic_name')
        subscription_name = kwargs.get('subscription_name')
        subject = kwargs.get('subject')
        message = kwargs.get('message')
        correlation_id = get_guid()
        logger.critical('Metro task exception. Message: %s, exception: %s, traceback: %s', message, str(exc), einfo)
        try:
            from metroid.models import FailedMessage

            FailedMessage.objects.create(
                topic_name=topic_name,
                subscription_name=subscription_name,
                subject=subject,
                message=message,
                exception_str=str(exc),
                traceback=str(einfo),
                correlation_id=correlation_id or '',
            )
            logger.info('Saved failed message to database.')
        except Exception as error:  # pragma: no cover
            # Should be impossible for this to happen (famous last words), but a nice failsafe.
            logger.exception('Unable to save Metro message. Error: %s', error)
