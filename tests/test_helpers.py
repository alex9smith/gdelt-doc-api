import unittest
from datetime import datetime

from gdeltdoc.helpers import format_date


class FormatDateTestCase(unittest.TestCase):
    def test_returns_string_input(self):
        date = "2020-01-01"
        self.assertEqual("20200101000000", format_date(date))

    def test_converts_a_datetime_to_string_in_correct_format(self):
        date = datetime(year=2020, month=1, day=1, hour=12, minute=30, second=30)
        self.assertEqual("20200101123030", format_date(date))
