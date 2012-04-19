
import mock
from unittest import TestCase, main


from .. import http

__all__ = (
    'ApiRequestTests',
)

class ApiStub(object):
    BASE_URL = "http://www.example.com"

    @http.api_request("/do-something-awesome/", timeout=10)
    def be_awesome(self):
        return {'level': 5}


class ApiRequestTests(TestCase):

    @mock.patch.object(http, "urlopen")
    def test_calls_url_open_with_full_url(self, urlopen):
        api = ApiStub()
        api.be_awesome()
        urlopen.assert_called_once_with("http://www.example.com/do-something-awesome/?level=5", timeout=10)


if __name__ == '__main__':
    main()

