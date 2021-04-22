import pandas as pd
import unittest

from gdeltdoc import GdeltDoc, Filters
from datetime import datetime, timedelta


class ArticleSearchTestCast(unittest.TestCase):
    """
    Test that the API client behaves correctly when doing an article search query
    """

    def setUp(self):
        self.start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.end_date = (datetime.today() - timedelta(days=6)).strftime("%Y-%m-%d")

        f = Filters(
            keyword="environment", start_date=self.start_date, end_date=self.end_date
        )
        self.articles = GdeltDoc().article_search(f)

    def tearDown(self):
        pass

    def test_articles_is_a_df(self):
        self.assertEqual(type(self.articles), pd.DataFrame)

    def test_correct_columns(self):
        self.assertEqual(
            list(self.articles.columns),
            [
                "url",
                "url_mobile",
                "title",
                "seendate",
                "socialimage",
                "domain",
                "language",
                "sourcecountry",
            ],
        )

    def test_rows_returned(self):
        # This test could fail if there really are no articles
        # that match the filter, but given the query used for
        # testing that's very unlikely.
        self.assertGreaterEqual(self.articles.shape[0], 1)


class TimelineSearchTestCase(unittest.TestCase):
    """
    Test that the various modes of timeline search behave corectly.
    """

    # Make one set of API calls per test suite run, not one per test
    @classmethod
    def setUpClass(self):
        self.start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        self.end_date = (datetime.today() - timedelta(days=6)).strftime("%Y-%m-%d")

        f = Filters(
            keyword="environment", start_date=self.start_date, end_date=self.end_date
        )

        gd = GdeltDoc()

        self.all_results = [
            gd.timeline_search(mode, f)
            for mode in [
                "timelinevol",
                "timelinevolraw",
                "timelinelang",
                "timelinetone",
                "timelinesourcecountry",
            ]
        ]

    @classmethod
    def tearDownClass(self):
        pass

    def test_all_modes_return_a_df(self):
        self.assertTrue(
            all([type(result) == pd.DataFrame for result in self.all_results])
        )

    def test_all_modes_return_data(self):
        self.assertTrue(all([result.shape[0] >= 1 for result in self.all_results]))

    def test_unsupported_mode(self):
        with self.assertRaisesRegex(ValueError, "not in supported API modes"):
            GdeltDoc().timeline_search(
                "unsupported",
                Filters(
                    keyword="environment",
                    start_date=self.start_date,
                    end_date=self.end_date,
                ),
            )

    def test_vol_has_two_columns(self):
        self.assertEqual(self.all_results[0].shape[1], 2)

    def test_vol_raw_has_three_columns(self):
        self.assertEqual(self.all_results[1].shape[1], 3)
