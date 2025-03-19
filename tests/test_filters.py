from gdeltdoc import (
    Filters,
    near,
    multi_near,
    repeat,
    multi_repeat,
    VALID_TIMESPAN_UNITS,
)

import unittest


class FiltersTestCase(unittest.TestCase):
    """
    Test that the correct query strings are generated from
    various filters.
    """

    def test_single_keyword_filter(self):
        f = Filters(keyword="airline", start_date="2020-03-01", end_date="2020-03-02")
        self.assertEqual(
            f.query_string,
            '"airline" &startdatetime=20200301000000&enddatetime=20200302000000&maxrecords=250',
        )

    def test_single_keyphrase_filter(self):
        f = Filters(
            keyword="climate change", start_date="2020-03-01", end_date="2020-03-02"
        )
        self.assertEqual(
            f.query_string,
            '"climate change" &startdatetime=20200301000000&enddatetime=20200302000000&maxrecords=250',
        )

    def test_multiple_keywords(self):
        f = Filters(
            keyword=["airline", "climate"],
            start_date="2020-05-13",
            end_date="2020-05-14",
        )
        self.assertEqual(
            f.query_string,
            "(airline OR climate) &startdatetime=20200513000000&"
            "enddatetime=20200514000000&maxrecords=250",
        )

    def test_multiple_themes(self):
        f = Filters(
            theme=["ENV_CLIMATECHANGE", "LEADER"],
            start_date="2020-05-13",
            end_date="2020-05-14",
        )
        self.assertEqual(
            f.query_string,
            "(theme:ENV_CLIMATECHANGE OR theme:LEADER) &startdatetime=20200513000000&"
            "enddatetime=20200514000000&maxrecords=250",
        )

    def test_theme_and_keyword(self):
        f = Filters(
            keyword="airline",
            theme="ENV_CLIMATECHANGE",
            start_date="2020-05-13",
            end_date="2020-05-14",
        )
        self.assertEqual(
            f.query_string,
            '"airline" theme:ENV_CLIMATECHANGE &startdatetime=20200513000000&'
            "enddatetime=20200514000000&maxrecords=250",
        )

    def test_tone_filter(self):
        f = Filters(
            keyword="airline",
            start_date="2020-03-01",
            end_date="2020-03-02",
            tone=">10",
        )
        self.assertEqual(
            f.query_string,
            '"airline" tone>10 &startdatetime=20200301000000&enddatetime=20200302000000&maxrecords=250',
        )


class NearTestCast(unittest.TestCase):
    """
    Test that `near()` generates the right filters and errors.
    """

    def test_two_words(self):
        self.assertEqual(near(5, "airline", "crisis"), 'near5:"airline crisis" ')

    def test_three_words(self):
        self.assertEqual(
            near(10, "airline", "climate", "change"), 'near10:"airline climate change" '
        )

    def test_one_word(self):
        with self.assertRaisesRegex(ValueError, "At least two words"):
            near(5, "airline")


class MultiNearTestCast(unittest.TestCase):
    """
    Test that `near()` generates the right filters and errors.
    """

    def test_single_near(self):
        self.assertEqual(
            multi_near([(5, "airline", "crisis")]), near(5, "airline", "crisis")
        )

    def test_two_nears(self):
        self.assertEqual(
            multi_near(
                [(5, "airline", "crisis"), (10, "airline", "climate", "change")]
            ),
            "("
            + near(5, "airline", "crisis")
            + "OR "
            + near(10, "airline", "climate", "change")
            + ") ",
        )

    def test_two_nears_AND(self):
        self.assertEqual(
            multi_near(
                [(5, "airline", "crisis"), (10, "airline", "climate", "change")],
                method="AND",
            ),
            near(5, "airline", "crisis")
            + "AND "
            + near(10, "airline", "climate", "change"),
        )


class RepeatTestCase(unittest.TestCase):
    """
    Test that `repeat()` generates the correct filters and errors.
    """

    def test_repeat(self):
        self.assertEqual(repeat(3, "environment"), 'repeat3:"environment" ')

    def test_repeat_phrase(self):
        with self.assertRaisesRegex(ValueError, "single word"):
            repeat(5, "climate change   ")


class MultiRepeatTestCase(unittest.TestCase):
    """
    Test that `multi_repeat() generates the correct filters and errors.
    """

    def test_multi_repeat(self):
        self.assertEqual(
            multi_repeat([(2, "airline"), (3, "airport")], "AND"),
            'repeat2:"airline" AND repeat3:"airport" ',
        )

    def test_multi_repeat_or(self):
        self.assertEqual(
            multi_repeat([(2, "airline"), (3, "airport")], "OR"),
            '(repeat2:"airline" OR repeat3:"airport" )',
        )

    def test_multi_repeat_checks_method(self):
        with self.assertRaisesRegex(ValueError, "method must be one of AND or OR"):
            multi_repeat([(2, "airline"), (3, "airport")], "NOT_A_METHOD")


class TimespanTestCase(unittest.TestCase):
    """
    Test that `Filter._validate_timespan` validates timespans correctly
    """

    def test_allows_valid_units(self):
        for unit in VALID_TIMESPAN_UNITS:
            try:
                Filters._validate_timespan(f"60{unit}")
            except ValueError:
                self.fail()

    def test_forbids_invalid_units(self):
        with self.assertRaisesRegex(ValueError, "is not a supported unit"):
            Filters._validate_timespan(f"60milliseconds")

    def test_forbids_invalid_values(self):
        invalid_timespans = ["12.5min", "40days0", "2/3weeks"]
        for timespan in invalid_timespans:
            with self.assertRaises(ValueError):
                Filters._validate_timespan(timespan)

    def test_forbids_incorrectly_formatted_timespans(self):
        with self.assertRaisesRegex(ValueError, "is not a supported unit"):
            Filters._validate_timespan(f"min15")

    def test_timespan_greater_than_60_mins(self):
        with self.assertRaisesRegex(ValueError, "Period must be at least 60 minutes"):
            Filters._validate_timespan(f"15min")


class ToneFilterToStringTestCase(unittest.TestCase):
    def test_single_tone(self):
        self.assertEqual(Filters._tone_to_string("tone", ">5"), "tone>5 ")

    def test_rejects_multiple_tones(self):
        with self.assertRaisesRegex(
            NotImplementedError, "Multiple tone values are not supported yet"
        ):
            Filters._tone_to_string("tone", [">5", "<10"])
