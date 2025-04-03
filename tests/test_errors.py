import unittest

from requests import Response, HTTPError
from gdeltdoc.errors import (
    HttpResponseCodes,
    raise_response_error,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ClientRequestError,
    ServerError,
)


def build_response(status_code: int) -> Response:
    response = Response()
    response._content = str.encode("text")
    response.status_code = status_code
    return response


class RaiseResponseErrorTestCase(unittest.TestCase):
    def test_doesnt_raise_when_status_200(self):
        raise_response_error(build_response(HttpResponseCodes.OK.value))

    def test_raises_bad_request_error_when_status_400(self):
        with self.assertRaises(BadRequestError):
            raise_response_error(build_response(HttpResponseCodes.BAD_REQUEST.value))

    def test_raises_not_found_error_when_status_404(self):
        with self.assertRaises(NotFoundError):
            raise_response_error(build_response(HttpResponseCodes.NOT_FOUND.value))

    def test_raises_rate_limit_error_when_status_429(self):
        with self.assertRaises(RateLimitError):
            raise_response_error(build_response(HttpResponseCodes.RATE_LIMIT.value))

    def test_raises_server_error_when_status_5XX(self):
        with self.assertRaises(ServerError):
            raise_response_error(build_response(503))

    def test_raises_client_error_when_status_4XX(self):
        with self.assertRaises(ClientRequestError):
            raise_response_error(build_response(403))

    def test_raises_http_error_when_status_unhandled(self):
        with self.assertRaises(HTTPError):
            raise_response_error(build_response(600))
