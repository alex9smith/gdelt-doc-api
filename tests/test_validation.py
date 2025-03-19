from gdeltdoc.validation import validate_tone
import unittest


class ValidateToneTestCase(unittest.TestCase):
    def valid_tone_doesnt_raise_error(self):
        validate_tone(">5")

    def raises_when_comparator_missing(self):
        with self.assertRaises(ValueError):
            validate_tone("10")

    def raises_when_equals_in_comparator(self):
        with self.assertRaises(ValueError):
            validate_tone(">=10")

    def raises_when_multiple_tones(self):
        with self.assertRaises(NotImplementedError):
            validate_tone([">5", "<10"])
