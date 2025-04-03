from enum import Enum, unique
from requests import Response, HTTPError


@unique
class HttpResponseCodes(Enum):
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    RATE_LIMIT = 429


class BadRequestError(HTTPError):
    """Raised when the response from the API is a 400 status"""


class NotFoundError(HTTPError):
    """Raised when the response from the API is a 404 status"""


class RateLimitError(HTTPError):
    """Raised when the response from the API is a 429 status"""


class ClientRequestError(HTTPError):
    """Raised when the response from the API is a 4XX status that's not 400, 404 or 429"""


class ServerError(HTTPError):
    """Raised when the response from the API is a 5XX status"""


def raise_response_error(response: Response) -> None:
    if response.status_code == HttpResponseCodes.OK.value:
        return

    elif response.status_code == HttpResponseCodes.BAD_REQUEST.value:
        raise BadRequestError(response=response)

    elif response.status_code == HttpResponseCodes.NOT_FOUND.value:
        raise NotFoundError(response=response)

    elif response.status_code == HttpResponseCodes.RATE_LIMIT.value:
        raise RateLimitError(response=response)

    elif response.status_code >= 400 and response.status_code < 500:
        raise ClientRequestError(response=response)

    elif response.status_code >= 500 and response.status_code < 600:
        raise ServerError(response=response)

    else:
        raise HTTPError(response=response)
