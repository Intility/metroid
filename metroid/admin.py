import logging

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

import requests

from metroid.config import settings
from metroid.models import FailedMessage, FailedPublishMessage

logger = logging.getLogger('metroid')


@admin.register(FailedMessage)
class FailedMessageAdmin(admin.ModelAdmin):
    readonly_fields = (
        'created',
        'correlation_id',
        'topic_name',
        'subject',
        'subscription_name',
        'message',
        'exception_str',
        'traceback',
    )
    list_display = ['id', 'correlation_id', 'topic_name', 'subject', 'created']

    actions = ['retry']

    def retry(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Retry a failed message.
        """
        for message in queryset:
            handler = settings.get_handler_function(
                topic_name=message.topic_name, subscription_name=message.subscription_name, subject=message.subject
            )
            if handler:
                try:
                    logger.info('Attempting to retry id %s', message.id)

                    if settings.worker_type == 'celery':
                        handler.apply_async(  # type: ignore
                            kwargs={
                                'message': message.message,
                                'topic_name': message.topic_name,
                                'subscription_name': message.subscription_name,
                                'subject': message.subject,
                            }
                        )
                    elif settings.worker_type == 'rq':
                        import django_rq

                        failed_job_registry = django_rq.get_queue('metroid').failed_job_registry
                        failed_job_registry.requeue(message.message.get('id'))

                    logger.info('Deleting %s from database', message.id)
                    message.delete()
                    logger.info('Returning')
                    self.message_user(
                        request=request,
                        message='Task has been retried.',
                        level=messages.SUCCESS,
                    )
                except Exception as error:
                    logger.exception('Unable to retry Metro message. Error: %s', error)
                    self.message_user(
                        request=request,
                        message=f'Unable to retry Metro message. Error: {error}',
                        level=messages.ERROR,
                    )
            else:
                logger.warning('No handler found for %s', message.id)
                self.message_user(
                    request=request,
                    message=f'No handler function found for id {message.id}.',
                    level=messages.WARNING,
                )
        return


@admin.register(FailedPublishMessage)
class FailedPublishMessageAdmin(admin.ModelAdmin):
    readonly_fields = (
        'correlation_id',
        'data',
        'data_version',
        'event_time',
        'event_type',
        'topic_name',
        'subject',
    )
    list_display = ['id', 'correlation_id', 'topic_name', 'subject', 'event_time']

    actions = ['retry_publish']

    def retry_publish(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Retry messages that failed to publish.
        """
        for message in queryset:
            try:
                metro_response = requests.post(
                    url=f'https://api.intility.no/metro/{message.topic_name}',
                    headers={
                        'content-type': 'application/json',
                        'x-metro-key': settings.get_x_metro_key(topic_name=message.topic_name),
                    },
                    data=message.data,
                )
                metro_response.raise_for_status()
                logger.info('Deleting %s from database', message.id)
                message.delete()
                logger.info('Posted to Metro')
                self.message_user(
                    request=request,
                    message='Message has been republished',
                    level=messages.SUCCESS,
                )
            except Exception as error:
                logger.exception('Unable to republish Metro message. Error: %s', error)
                self.message_user(
                    request=request,
                    message=f'Unable to republish Metro message. Error: {error}',
                    level=messages.ERROR,
                )
        return
