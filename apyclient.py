# apyclient.py
# A python client api library.
# Copyright (C) 2012 Aaron Madison

# Released subject to the BSD License


__all__ = (
    'api_request',
    'BaseResponse',
    'JSONApiResponse',
)

__version__ = "0.0.1"


from functools import wraps
import json
import socket
from urllib import urlencode
import urllib2


class BaseResponse(object):
    """
    Thin wrapper around response that comes back from urlopen.
    Mainly just so you can easily extend the response if desired.

    Note that this response is not EXACTLY like a response you'd normally
    get from urlopen. It cannot be used as a drop in replacement.
    """
    _content = None

    def __init__(self, response):
        self.original_response = response

    @property
    def code(self):
        return self.original_response.code

    @property
    def is_success(self):
        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, and accepted.
        return self.code // 100 == 2

    @property
    def content(self):
        """
        Returns raw response content.
        """
        if self._content is None:
            self._content = self.original_response.read()
        return self._content


def api_request(endpoint, method="GET", timeout=socket._GLOBAL_DEFAULT_TIMEOUT, response_class=None):
    """
    Decorator to turn method into api call.
    Assumes parent class has "HOST_NAME" defined.

    Check tests / docs for usage.

    :param endpoint:
        URL endpoint for request.

    :param method:
        HTTP method for request.

    :param timeout:
        Timeout in seconds.

    :param response_class:
        Response class to wrap response in. If not provided will use standard response from urlopen,
        or standard HttpError if received.
    """

    def _outter(func):
        @wraps(func)
        def _inner(cls, *args, **kwargs):
            try:
                url = cls.HOST_NAME + endpoint
                func_data = func(cls, *args, **kwargs)
                query_data = urlencode(func_data, doseq=1)
                if method == "GET":
                    url += "?" + query_data
                    query_data = None

                response = urllib2.urlopen(url, data=query_data, timeout=timeout)
            except urllib2.HTTPError as e:
                response = e

            custom_response = response_class or getattr(cls, "RESPONSE_CLASS", None)
            if custom_response:
                return custom_response(response)
            else:
                return response
        return _inner
    return _outter



class JSONApiResponse(BaseResponse):
    """
    Loads JSON object from Response.

    You still need to be careful that the response is a json string in the
    first place (you didn't get some crazy non-json error)
    """
    _json = None

    def json(self):
        if self._json is None:
            self._json = json.loads(self.content)
        return self._json




