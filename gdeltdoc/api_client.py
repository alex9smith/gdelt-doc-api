import requests
import pandas as pd

from gdeltdoc.filters import Filters

from typing import Dict


class GdeltDoc:
    def __init__(self) -> None:
        """
        API client for the GDELT 2.0 Doc API

        ```
        from gdeltdoc import GdeltDoc, Filters

        f = Filters(
            keyword = "climate change",
            start_date = "2020-05-10",
            end_date = "2020-05-11"
        )

        gd = GdeltDoc()

        # Search for articles matching the filters
        articles = gd.article_search(f)

        # Get a timeline of the number of articles matching the filters
        timeline = gd.timeline_search("timelinevol", f)
        ```

        ### Article List
        The article list mode of the API generates a list of news articles that match the filters. The client returns this as a pandas DataFrame with columns `url`, `url_mobile`, `title`, `seendate`, `socialimage`, `domain`, `language`, `sourcecountry`.

        ### Timeline Search
        There are 5 available modes when making a timeline search:
        * `timelinevol` - a timeline of the volume of news coverage matching the filters, represented as a percentage of the total news articles monitored by GDELT.
        * `timelinevolraw` - similar to `timelinevol`, but has the actual number of articles and a total rather than a percentage
        * `timelinelang` - similar to `timelinevol` but breaks the total articles down by published language. Each language is returned as a separate column in the DataFrame.
        * `timelinesourcecountry` - similar to `timelinevol` but breaks the total articles down by the country they were published in. Each country is returned as a separate column in the DataFrame.
        * `timelinetone` - a timeline of the average tone of the news coverage matching the filters. See [GDELT's documentation](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) for more information about the tone metric.
        """
        pass

    def article_search(self, filters: Filters) -> pd.DataFrame:
        """
        Make a query against the `ArtList` API to return a DataFrame of news articles that
        match the supplied filters.

        Params
        ------
        filters
            A `gdelt-doc.Filters` object containing the filter parameters for this query.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame of the articles returned from the API.
        """
        articles = self._query("artlist", filters.query_string)

        return pd.DataFrame(articles["articles"])

    def timeline_search(self, mode: str, filters: Filters) -> pd.DataFrame:
        """
        Make a query using one of the API's timeline modes.

        Params
        ------
        mode
            The API mode to call. Must be one of "timelinevol", "timelinevolraw",
            "timelinetone", "timelinelang", "timelinesourcecountry".

            See https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/ for a
            longer description of each mode.

        filters
            A `gdelt-doc.Filters` object containing the filter parameters for this query.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame of the articles returned from the API.
        """
        timeline = self._query(mode, filters.query_string)

        results = {}
        results["datetime"] = [
            entry["date"] for entry in timeline["timeline"][0]["data"]
        ]

        for series in timeline["timeline"]:
            results[series["series"]] = [entry["value"] for entry in series["data"]]

        if mode == "timelinevolraw":
            results["All Articles"] = [
                entry["norm"] for entry in timeline["timeline"][0]["data"]
            ]

        formatted = pd.DataFrame(results)
        formatted["datetime"] = pd.to_datetime(formatted["datetime"])

        return formatted

    def _query(self, mode: str, query_string: str) -> Dict:
        """
        Submit a query to the GDELT API and return the results as a parsed JSON object.

        Params
        ------
        mode
            The API mode to call. Must be one of "artlist", "timelinevol",
            "timelinevolraw", "timelinetone", "timelinelang", "timelinesourcecountry".

        query_string
            The query parameters and date range to call the API with.

        Returns
        -------
        Dict
            The parsed JSON response from the API.
        """
        if mode not in [
            "artlist",
            "timelinevol",
            "timelinevolraw",
            "timelinetone",
            "timelinelang",
            "timelinesourcecountry",
        ]:
            raise ValueError(f"Mode {mode} not in supported API modes")

        return requests.get(
            f"https://api.gdeltproject.org/api/v2/doc/doc?query={query_string}&mode={mode}&format=json"
        ).json()
