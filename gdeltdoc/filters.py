from typing import Optional, List, Union, Tuple, Unpack
from string import ascii_lowercase, digits
from gdeltdoc.validation import validate_tone

Filter = Union[List[str], str]

VALID_TIMESPAN_UNITS = ["min", "h", "hours", "d", "days", "w", "weeks", "m", "months"]


def near(n: int, *args) -> str:
    """
    Build the filter to find articles containing words that occur within
    `n` words of each other.

    eg. near(5, "airline", "climate") finds articles containing both
    "airline" and "climate" within 5 words.
    """
    if len(args) < 2:
        raise ValueError("At least two words must be provided")

    return f"near{str(n)}:" + '"' + " ".join([a for a in args]) + '" '


def multi_near(
    nears: List[Tuple[int, Unpack[Tuple[str, ...]]]], method: str = "OR"
) -> str:
    """
    Build the filter to find articles containing multiple sets of near terms.

    eg. multi_near([(5, "airline", "crisis"), (10, "airline", "climate", "change")]) finds "airline" and "crisis"
    within 5 words, and/or "airline", "climate", and "change" within 10 words
    """
    if method not in ["AND", "OR"]:
        raise ValueError(f"method must be one of AND or OR, not {method}")

    formatted = [near(n, *args) for (n, *args) in nears]

    paren_flag = len(formatted) != 1 and method == "OR"
    l_pad, r_pad = paren_flag * "(", paren_flag * ") "

    return l_pad + f"{method} ".join(formatted) + r_pad


def repeat(n: int, keyword: str) -> str:
    """
    Build the filter to find articles containing `keyword` at least `n` times.

    eg. repeat(2, "environment") finds articles containing the word "environment"
    at least twice.

    Only single word repetitions are allowed.
    """
    if " " in keyword:
        raise ValueError("Only single words can be repeated")

    return f'repeat{str(n)}:"{keyword}" '


def multi_repeat(repeats: List[Tuple[int, str]], method: str) -> str:
    """
    Build the filter to find articles containing multiple repeated words using `repeat()`

    eg. multi_repeat([(2, "airline"), (3, "airport")], "AND") finds articles that contain the word "airline" at least
    twice and "airport" at least 3 times.

    Params
    ------
        repeats: A list of (int, str) tuples to be passed to `repeat()`. Eg. [(2, "airline"), (3, "airport")]
        method: How to combine the restrictions. Must be one of "AND" or "OR"
    """
    if method not in ["AND", "OR"]:
        raise ValueError(f"method must be one of AND or OR, not {method}")

    to_repeat = [repeat(n, keyword) for (n, keyword) in repeats]

    if method == "AND":
        return f"{method} ".join(to_repeat)
    else:
        # method == "OR"
        return "(" + f"{method} ".join(to_repeat) + ")"


class Filters:
    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timespan: Optional[str] = None,
        num_records: int = 250,
        keyword: Optional[Filter] = None,
        domain: Optional[Filter] = None,
        domain_exact: Optional[Filter] = None,
        near: Optional[str] = None,
        repeat: Optional[str] = None,
        country: Optional[Filter] = None,
        language: Optional[Filter] = None,
        theme: Optional[Filter] = None,
        tone: Optional[Filter] = None,
        tone_absolute: Optional[Filter] = None,
    ) -> None:
        """
        Construct filters for the GDELT API.

        Filters for `keyword`, `domain`, `domain_exact`, `country` and `theme`
        can be passed either as a single string or as a list of strings. If a list is
        passed, the values in the list are wrapped in a boolean OR.

        Params
        ------
        start_date
            The start date for the filter in YYYY-MM-DD format. The API officially only supports the
            most recent 3 months of articles. Making a request for an earlier date range may still
            return data, but it's not guaranteed.
            Must provide either `start_date` and `end_date` or `timespan`

        end_date
            The end date for the filter in YYYY-MM-DD format.

        timespan
            A timespan to search for, relative to the time of the request. Must match one of the API's timespan
            formats - https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
            Must provide either `start_date` and `end_date` or `timespan`

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
            If you want to construct a filter with multiple repeated words, construct with `multi_repeat()`
            instead. eg. repeat = multi_repeat([(2, "airline"), (3, "airport")], "AND")

        country
            Return articles published in a country, formatted as the FIPS 2 letter country code.

        language
            Return articles published in the given language, formatted as the ISO 639 language code.

        theme
            Return articles that cover one of GDELT's GKG Themes. A full list of themes can be
            found here: http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT

        tone
            Return articles above or below a particular tone score (ie more positive or more negative than
            a certain threshold). To use, specify either a greater than or less than sign and a positive
            or negative number (either an integer or floating point number). To find fairly positive
            articles, search for "tone>5" or to search for fairly negative articles, search for "tone<-5"

        tone_absolute
            The same as `tone` but ignores the positive/negative sign and lets you simply search for
            high emotion or low emotion articles, regardless of whether they were happy or sad in tone
        """
        self.query_params: List[str] = []
        self._valid_countries: List[str] = []
        self._valid_themes: List[str] = []

        # Check we have either start/end date or timespan, but not both
        if not start_date and not end_date and not timespan:
            raise ValueError("Must provide either start_date and end_date, or timespan")

        if start_date and end_date and timespan:
            raise ValueError(
                "Can only provide either start_date and end_date, or timespan"
            )

        if keyword:
            self.query_params.append(self._keyword_to_string(keyword))

        if domain:
            self.query_params.append(self._filter_to_string("domain", domain))

        if domain_exact:
            self.query_params.append(self._filter_to_string("domainis", domain_exact))

        if country:
            self.query_params.append(self._filter_to_string("sourcecountry", country))

        if language:
            self.query_params.append(self._filter_to_string("sourcelang", language))

        if theme:
            self.query_params.append(self._filter_to_string("theme", theme))

        if tone:
            validate_tone(tone)
            self.query_params.append(self._tone_to_string("tone", tone))

        if tone_absolute:
            validate_tone(tone_absolute)
            self.query_params.append(self._tone_to_string("toneabs", tone_absolute))

        if near:
            self.query_params.append(near)

        if repeat:
            self.query_params.append(repeat)

        if start_date:
            if not end_date:
                raise ValueError("Must provide both start_date and end_date")

            self.query_params.append(
                f'&startdatetime={start_date.replace("-", "")}000000'
            )
            self.query_params.append(f'&enddatetime={end_date.replace("-", "")}000000')

        elif timespan:
            self._validate_timespan(timespan)
            self.query_params.append(f"&timespan={timespan}")

        if num_records > 250:
            raise ValueError(f"num_records must 250 or less, not {num_records}")

        self.query_params.append(f"&maxrecords={str(num_records)}")

    @property
    def query_string(self) -> str:
        return "".join(self.query_params)

    @staticmethod
    def _filter_to_string(name: str, f: Filter) -> str:
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
            return f"{name}:{f} "

        else:
            # Build an OR statement
            return "(" + " OR ".join([f"{name}:{clause}" for clause in f]) + ") "

    @staticmethod
    def _keyword_to_string(keywords: Filter) -> str:
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
            return f'"{keywords}" '

        else:
            return (
                "("
                + " OR ".join(
                    [f'"{word}"' if " " in word else word for word in keywords]
                )
                + ") "
            )

    @staticmethod
    def _tone_to_string(name: str, tone: Filter) -> str:
        """
        Convert a Filter for tone or tone_absolute into the string for the API.
        Tone is different to the other parameters because it has no colon between
        the API parameter and the value.

        Params
        ------
        name
            The parameter name as required by the API. Must be either `tone` or `toneabs`
        tone
            The tone Filter

        Returns
        -------
        str
            The converted filter eg. "tone>5"
        """
        if type(tone) == str:
            return f"{name}{tone} "

        else:
            raise NotImplementedError("Multiple tone values are not supported yet.")

    @staticmethod
    def _validate_timespan(timespan: str) -> None:
        """
        Validate that the supplied timespan is in a format recognised by the API.
        Raises a `ValueError` if the timespan is not recognised.

        Supported timespan units are:
            - minutes - 15min
            - hours - 24h or 24hours
            - days - 30d or 30days
            - months - 2m or 2months

        Params
        ------
        timespan
            The timespan filter to be checked

        Returns
        -------
        None
        """

        value = timespan.rstrip(ascii_lowercase)
        unit = timespan[len(value) :]

        if unit not in VALID_TIMESPAN_UNITS:
            raise ValueError(
                f"Timespan {timespan} is invalid. {unit} is not a supported unit, must be one of {' '.join(VALID_TIMESPAN_UNITS)}"
            )

        if not all(d in digits for d in value):
            raise ValueError(
                f"Timespan {timespan} is invalid. {value} could not be converted into an integer"
            )

        if unit == "min" and int(value) < 60:
            raise ValueError(
                f"Timespan {timespan} is invalid. Period must be at least 60 minutes"
            )
