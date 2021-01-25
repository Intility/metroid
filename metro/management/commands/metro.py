import asyncio
import logging
from asyncio.exceptions import InvalidStateError
from asyncio.tasks import Task

from django.core.management.base import BaseCommand

from metro.config import settings
from metro.subscribe import subscribe_to_topic

logger = logging.getLogger('metro')


class Command(BaseCommand):
    help = (
        'Starts a subscription asyncio loop for each subscription configured in your settings.'
        'When a message we expect is received, a Celery Worker task will be spawned to handle that message.'
        'The message will be marked as deferred, and the Celery task must then complete the message.'
    )

    @staticmethod
    async def start_tasks() -> None:
        """
        Creates background tasks to subscribe to events
        """
        tasks: list[Task] = [
            asyncio.create_task(
                subscribe_to_topic(
                    connection_string=subscription['connection_string'],
                    topic_name=subscription['topic_name'],
                    subscription_name=subscription['subscription_name'],
                    handlers=subscription['handlers'],
                )
            )
            for subscription in settings.subscriptions
        ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)  # Also covers FIRST_EXCEPTION

        # Log why the task ended
        for task in done:
            try:
                raise task.exception()  # type: ignore # We do this to use `logger.exception` which enables trace nicely
            except InvalidStateError:
                logger.critical('Task %s ended early without an exception', task)
            except Exception as error:
                logger.exception('Exception in subscription task %s. Exception: %s', task, error)

        for task in pending:
            # cancel all remaining running tasks. This kills the service (and container)
            task.cancel()

    def handle(self, *args: None, **options) -> None:
        """
        This function is called when `manage.py runmetro` is run from the terminal.

        Spawns a process to handle incoming messages from a Metro subscription for each subscription configured in "***REMOVED***".
        """
        logger.info('Starting Metro subscriptions')
        asyncio.run(self.start_tasks())
