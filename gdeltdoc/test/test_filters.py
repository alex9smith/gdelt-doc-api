from gdeltdoc import Filters, near, repeat, multi_repeat

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
            '"airline"&startdatetime=20200301000000&enddatetime=20200302000000&maxrecords=250',
        )

    def test_single_keyphrase_filter(self):
        f = Filters(
            keyword="climate change", start_date="2020-03-01", end_date="2020-03-02"
        )
        self.assertEqual(
            f.query_string,
            '"climate change"&startdatetime=20200301000000&enddatetime=20200302000000&maxrecords=250',
        )

    def test_multiple_keywords(self):
        f = Filters(
            keyword=["airline", "climate"],
            start_date="2020-05-13",
            end_date="2020-05-14",
        )
        self.assertEqual(
            f.query_string,
            "(airline OR climate)&startdatetime=20200513000000&enddatetime=20200514000000&maxrecords=250",
        )

    def test_multiple_themes(self):
        f = Filters(
            theme=["ENV_CLIMATECHANGE", "LEADER"],
            start_date="2020-05-13",
            end_date="2020-05-14",
        )
        self.assertEqual(
            f.query_string,
            "(theme:ENV_CLIMATECHANGE OR theme:LEADER)&startdatetime=20200513000000&enddatetime=20200514000000&maxrecords=250",
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
            '"airline"theme:ENV_CLIMATECHANGE&startdatetime=20200513000000&enddatetime=20200514000000&maxrecords=250',
        )

    def test_multiple_repeats(self):
        f = Filters(
            keyword="airline",
            repeat=multi_repeat([(3, "plane"), (2, "airport")], "OR"),
            start_date="2020-05-13",
            end_date="2020-05-14",
        )
        self.assertEqual(
            f.query_string,
            '"airline"repeat3:"plane"ORrepeat2:"airport"&startdatetime=20200513000000&enddatetime=20200514000000&maxrecords=250',
        )

    def test_timespan(self):
        f = Filters(keyword="airline", timespan="FULL")
        self.assertEqual(f.query_string, '"airline"&timespan=FULL&maxrecords=250')


class NearTestCast(unittest.TestCase):
    """
    Test that `near()` generates the right filters and errors.
    """

    def test_two_words(self):
        self.assertEqual(near(5, "airline", "crisis"), 'near5:"airline crisis"')

    def test_three_words(self):
        self.assertEqual(
            near(10, "airline", "climate", "change"), 'near10:"airline climate change"'
        )

    def test_one_word(self):
        with self.assertRaisesRegex(ValueError, "At least two words"):
            near(5, "airline")


class RepeatTestCase(unittest.TestCase):
    """
    Test that `repeat()` generates the correct filters and errors.
    """

    def test_repeat(self):
        self.assertEqual(repeat(3, "environment"), 'repeat3:"environment"')

    def test_repeat_phrase(self):
        with self.assertRaisesRegex(ValueError, "single word"):
            repeat(5, "climate change   ")
