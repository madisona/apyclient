
import json
from functools import wraps
import socket
from urllib import urlencode
from urllib2 import urlopen, HTTPError

def api_request(endpoint, method="GET", response_type="json", timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    """
    Class method wrapper
    """
    # todo: enhance to allow post method

    def _outter(func):
        @wraps(func)
        def _inner(cls, *args, **kwargs):
            try:
                data = func(cls, *args, **kwargs)
                url = cls.BASE_URL + endpoint + "?" + urlencode(data)
                r = urlopen(url, timeout=10)
                return json.loads(r.read())
            except HTTPError as e:

                # todo: log error
                return {}
        return _inner
    return _outter


class JSONApiResponse(object):
    """
    Thin wrapper for Response from urllib.


    """
    _content = None
    _json = None

    def __init__(self, response=None):
        self._response = response

    def __getattr__(self, item):
        """
        Allows you to get attributes straight from json response.
        (pass through to json response's get item)
        """

    @property
    def is_success(self):
        """
        Not error and response status code // 100 == 2
        """

    @property
    def status_code(self):
        pass

    @property
    def content(self):
        """
        return response body. Cache it
        """
        pass


