import logging

from django_guid import get_guid

from rq.job import Job

logger = logging.getLogger('metroid')


def on_failure(job: Job, *exc_info) -> bool:
    """
    Custom exception handler for Metro RQ tasks.
    This function must be added as a custom exception handler in django-rq RQ_EXCEPTION_HANDLERS settings

    :param job: RQ Job that has failed
    :param exc_info: Exception Info, tuple of exception type, value and traceback
    """
    if job.origin == 'metroid':
        topic_name = job.kwargs.get('topic_name')
        subscription_name = job.kwargs.get('subscription_name')
        subject = job.kwargs.get('subject')
        message = job.kwargs.get('message')
        correlation_id = get_guid()
        logger.critical(
            'Metro task exception. Message: %s, exception: %s, traceback: %s',
            message,
            str(exc_info[1]),
            exc_info,
        )
        try:
            from metroid.models import FailedMessage

            FailedMessage.objects.create(
                topic_name=topic_name,
                subscription_name=subscription_name,
                subject=subject,
                message=message,
                exception_str=str(exc_info[1]),
                traceback=str(exc_info),
                correlation_id=correlation_id or '',
            )
            logger.info('Saved failed message to database.')
        except Exception as error:  # pragma: no cover
            # Should be impossible for this to happen (famous last words), but a nice failsafe.
            logger.exception('Unable to save Metro message. Error: %s', error)
        # Return false to stop processing exception
        return False
    else:
        # Return true to send exception to next handler
        return True
