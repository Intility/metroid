from django.core.exceptions import ImproperlyConfigured

import pytest

from metroid.subscribe import match_handler_subject


def test_valid_pattern() -> None:
    """
    Tests if a valid pattern matches  the provided subject.
    """
    subject = r'^something\/tests\/haha.*$'
    subject_in_message = 'something/tests/haha/asd-123'
    is_match = match_handler_subject(subject=subject, message_subject=subject_in_message, is_regex=True)
    assert is_match is True


def test_wrong_subject_match_on_pattern() -> None:
    """
    Tests if the validation fails if not a matching reggex is provided.
    """
    subject = r'^something\/tests\/haha.*$'
    subject_in_message = 'tests/haha/asd-123'
    is_match = match_handler_subject(subject=subject, message_subject=subject_in_message, is_regex=True)
    assert is_match is False


def test_match_on_string() -> None:
    """
    Tests if the pattern matches the subject provided in string format.
    """
    subject = 'tests/haha.Create'
    subject_in_message = 'tests/haha.Create'
    is_match = match_handler_subject(subject=subject, message_subject=subject_in_message, is_regex=False)
    assert is_match is True


def test_bogus_string() -> None:
    """
    Tests  if a very weird string with special characters matches .
    """
    subject = 'tests/haha$somethi#ngth"atshoul,-,.dn/otbehere'
    subject_in_message = 'tests/haha$somethi#ngth"atshoul,-,.dn/otbehere'
    is_match = match_handler_subject(subject=subject, message_subject=subject_in_message, is_regex=False)
    assert is_match is True


def test_if_exception_is_thrown() -> None:
    """
    Tests if the correct exception is thrown upon providing an invalid regex.
    """
    with pytest.raises(ImproperlyConfigured) as e:
        subject = 'tests/invalid['
        subject_in_message = 'tests/invalid['
        is_match = match_handler_subject(subject=subject, message_subject=subject_in_message, is_regex=True)
    assert str(e.value) == f'Provided regex pattern: {subject} is invalid.'
