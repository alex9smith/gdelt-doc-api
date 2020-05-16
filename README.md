# GDELT 2.0 Doc API Client

A Python client to fetch data from the [GDELT 2.0 Doc API](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/).

This allows for simpler, small-scale analysis of news coverage without having to deal with the complexities of downloading and managing the raw files from S3, or working with the BigQuery export.

## Installation

`gdeltdoc` is on PyPi and is installed through pip:

```bash
pip install gdeltdoc
```

## Use
The `ArtList` and `Timeline*` query modes are supported. 

```python
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

### Filters
The search query passed to the API is constructed from a `gdeltdoc.Filters` object. 

```python
from gdeltdoc import Filters, near, repeat

f = Filters(
    start_date = "2020-05-01",
    end_date = "2020-05-02",
    num_records = 250,
    keyword = "climate change",
    domain = ["bbc.co.uk", "nytimes.com"],
    country = ["UK", "US"],
    theme = "GENERAL_HEALTH,
    near = near(10, "airline", "carbon"),
    repeat = repeat(5, "planet")
)
```

Filters for `keyword`, `domain`, `domain_exact`, `country` and `theme` can be passed either as a single string or as a list of strings. If a list is passed, the values in the list are wrappeed in a boolean OR.

* `start_date` - Required - The start date for the filter in YYYY-MM-DD format. The API officially only supports the most recent 3 months of articles. Making a request for an earlier date range may still return data, but it's not guaranteed.
* `end_date` - Required - The end date for the filter in YYYY-MM-DD format.
* `num_records` - The number of records to return. Only used in article list mode and can be up to 250.
* `keyword` - Return articles containing the exact phrase `keyword` within the article text.
* `domain` - Return articles from the specified domain. Does not require an exact match so passing "cnn.com" will match articles from `cnn.com`, `subdomain.cnn.com` and `notactuallycnn.com`.
* `domain_exact` - Similar to `domain`, but requires an exact match.
* `country` - Return articles published in a country or list of countries, formatted as the FIPS 2 letter country code.
* `theme` - Return articles that cover one of GDELT's GKG Themes. A full list of themes can be found [here](http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT)
* `near` - Return articles containing words close to each other in the text. Use `near()` to construct. eg. `near = near(5, "airline", "climate")`.
* `repeat` - Return articles containing a single word repeated at least a number of times. Use `repeat()` to construct. eg. `repeat = repeat(3, "environment")`.