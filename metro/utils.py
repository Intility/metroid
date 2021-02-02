import re
from typing import Pattern, Union, Callable, Any


def get_subject_pattern(subject: Union[str, None, Callable[..., Any]]) -> Pattern:
    """
    Returns a reggex compile object which can be used to match the subject. A valid reggex pattern is compiled,
    or a string is escaped. There are some scenarios where it might not match, check the test "test_bogus_string".
    """
    try:
        return re.compile(subject)
    except re.error:
        return re.compile(re.escape(str(subject)))
