import logging
import re

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger('metroid')


def match_handler_subject(
    subject: str,
    message_subject: str,
    is_regex: bool,
) -> bool:
    """
    Checks if the provided message subject matches the handler's subject. Performs a match by using the regular
    expression, or compares strings based on  handler settings defined in settings.py.

    """
    if is_regex:
        try:
            pattern = re.compile(subject)
            return bool(re.match(pattern=pattern, string=message_subject))
        except re.error:
            raise ImproperlyConfigured(f'Provided regex pattern: {subject} is invalid.')
    else:
        return subject == message_subject
