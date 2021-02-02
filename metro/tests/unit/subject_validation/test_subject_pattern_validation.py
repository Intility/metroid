from django.test import TestCase

from metro.subscribe import get_subject_pattern


class TestSubjectPatternValidation(TestCase):
    """Did not use subtests to show the different scenarios with comments"""

    def test_valid_pattern(self) -> None:
        """
        Tests if a valid pattern matches  the provided subject.

        """
        subject = r'^***REMOVED***.*$'
        subject_in_message = '***REMOVED***'
        pattern = get_subject_pattern(subject)
        self.assertIsNotNone(pattern.match(subject_in_message))

    def test_wrong_subject_match_on_pattern(self) -> None:
        """
        Tests if the validation fails if not a matching reggex is provided.
        """
        subject = r'^***REMOVED***.*$'
        subject_in_message = '***REMOVED***'
        pattern = get_subject_pattern(subject)
        self.assertIsNone(pattern.match(subject_in_message))

    def test_match_on_string(self) -> None:
        """
        Tests if the pattern matches the subject provided in string format.
        """
        subject_in_message = 'tests/haha'
        pattern = get_subject_pattern(subject_in_message)
        self.assertIsNotNone(pattern.match(subject_in_message))

    def test_bogus_string(self) -> None:
        """
        Tests bogus string, it should actually match, but does not due to the character $.
        """
        subject_in_message = 'tests/haha$somethingthatshouldnotbehere'
        pattern = get_subject_pattern(subject_in_message)
        self.assertIsNone(pattern.match(subject_in_message))
