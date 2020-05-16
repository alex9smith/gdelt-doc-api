import requests

from typing import Optional, List, Union, Tuple

Filter = Union[List[str], str]

def near(n: int, *args) -> str:
    """
    Build the filter to find articles containing words that occur within
    `n` words of each other.

    eg. near(5, "airline", "climate") finds articles containing both
    "airline" and "climate" within 5 words.
    """
    if len(args) < 2:
        raise ValueError("At least two words must be provided")

    return f"near{str(n)}:" + '"' + " ".join([a for a in args]) + '"'


def repeat(n: int, keyword: str) -> str:
    """
    Build the filter to find articles containing `keyword` at least `n` times.

    eg. repeat(2, "environment") finds articles containing the word "environment"
    at least twice.
    
    Only single word repetitions are allowed.
    """
    if " " in keyword:
        raise ValueError("Only single words can be repeated")

    return f'repeat{str(n)}:"{keyword}"'


class Filters:
    def __init__(
        self,
        start_date: str,
        end_date: str,
        num_records: int = 250,
        keyword: Optional[Filter] = None,
        domain: Optional[Filter] = None,
        domain_exact: Optional[Filter] = None,
        near: Optional[str] = None,
        repeat: Optional[str] = None,
        country: Optional[Filter] = None,
        theme: Optional[Filter] = None
    ) -> None:
        """
        Construct filters for the GDELT API.

        Filters for `keyword`, `domain`, `domain_exact`, `country` and `theme`
        can be passed either as a single string or as a list of strings. If a list is
        passed, the values in the list are wrappeed in a boolean OR.

        Params
        ------
        start_date
            The start date for the filter in YYYY-MM-DD format. The API officially only supports the 
            most recent 3 months of articles. Making a request for an earlier date range may still
            return data, but it's not guaranteed.

        end_date
            The end date for the filter in YYYY-MM-DD format.

        num_records
            The number of records to return. Only used in article list mode and can be up to 250.

        keyword
            Return articles containing the exact phrase `keyword` within the article text.

        domain
            Return articles from the specified domain. Does not require an exact match so
            passing "cnn.com" will match articles from "cnn.com", "subdomain.cnn.com" and "notactuallycnn.com".

        domain_exact
            Similar to `domain`, but requires an exact match.

        near
            Return articles containing words close to each other in the text. Use `near()` to construct.
            eg. near = near(5, "airline", "climate").

        repeat
            Return articles containing a single word repeated at least a number of times. Use `repeat()`
            to construct. eg. repeat = repeat(3, "environment").

        country
            Return articles published in a country, formatted as the FIPS 2 letter country code.

        theme
            Return articles that cover one of GDELT's GKG Themes. A full list of themes can be
            found here: http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT
        """
        self.query_params: List[str] = []
        self._valid_countries: List[str] = []
        self._valid_themes: List[str] = []

        if keyword:
            self.query_params.append(self._keyword_to_string(keyword))

        if domain:
            self.query_params.append(self._filter_to_string("domain", domain))

        if domain_exact:
            self.query_params.append(self._filter_to_string("domainis", domain_exact))

        if country:
            self.query_params.append(self._filter_to_string("sourcecountry", country))

        if theme:
            self.query_params.append(self._filter_to_string("theme", theme))
        
        if near:
            self.query_params.append(near)

        if repeat:
            self.query_params.append(repeat)

        self.query_params.append(f'&startdatetime={start_date.replace("-", "")}000000')
        self.query_params.append(f'&enddatetime={end_date.replace("-", "")}000000')

        if num_records > 250:
            raise ValueError(f"num_records must 250 or less, not {num_records}")

        self.query_params.append(f"&maxrecords={str(num_records)}")        

    @property
    def query_string(self) -> str:
        return "".join(self.query_params)


    def _filter_to_string(self, name: str, f: Filter) -> str:
        """
        Convert a Filter into the string representation needed for the API.

        Params
        ------
        name
            The filter name as required by the API

        f
            The Filter to convert

        Returns
        -------
        str
            The converted filter. Eg. "domain:cnn.com"
        """
        if type(f) == str:
            return f"{name}:{f}"

        else:
            # Build an OR statement
            return "(" + " OR ".join([f"{name}:{clause}" for clause in f]) + ")"


    def _keyword_to_string(self, keywords: Filter) -> str:
        """
        Convert a Filter for keywords into the string for the API.
        The keyword argument is different to all the others in that there's
        no parameter name needed and if a key phrase is passed it
        must be wrapped in quotes.

        Params
        ------
        keyword
            The keyword Filter

        Returns
        -------
        str
            The converted filter eg. "(airline OR shipping)"
        """
        if type(keywords) == str:
            return f'"{keywords}"'

        else:
            return '('  + " OR ".join([f'"{word}"' if " " in word else word for word in keywords]) + ')'