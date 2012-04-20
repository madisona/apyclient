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


class APIRequest(object):
    """
    API method decorator to turn method into easy API call.
    Assumes parent class has "HOST_NAME" defined.
    """

    def __init__(self, endpoint, method="GET", timeout=socket._GLOBAL_DEFAULT_TIMEOUT, response_class=None):
        """
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
        self.endpoint = endpoint
        self.method = method
        self.timeout = timeout
        self.response_class = response_class

    def __call__(self, method):
        """
        Method being wrapped should only return data to be used for
        API call. The api_request takes that data, urlencodes it and
        makes the proper get or post request to the specified endpoint.
        """

        @wraps(method)
        def _inner(cls, *args, **kwargs):
            try:
                method_data = method(cls, *args, **kwargs)
                url, query_data = self._get_url_and_data(method_data, cls)
                response = self._open_url(url, query_data)
            except urllib2.HTTPError as e:
                response = e
            return self.prepare_response(response, cls)

        return _inner

    def _get_url_and_data(self, method_data, cls):
        """
        Returns url and data ready to make request.

        :param method_data:
            The data returned from the wrapped method call
        :param cls:
            The API class object being decorated.
        """
        url = cls.HOST_NAME + self.endpoint
        query_data = method_data and urlencode(method_data, doseq=1)
        if self.method == "GET" and query_data:
            url += "?" + query_data
            query_data = None
        return url, query_data

    def _open_url(self, url, query_data):
        return urllib2.urlopen(url, data=query_data, timeout=self.timeout)

    def prepare_response(self, response, cls):
        """
        Prepares API response for final return.

        :param response:
            The raw response returned from ``urlopen``
        :param cls:
            The API class object being decorated.
        """
        custom_response = self.response_class or getattr(cls, "RESPONSE_CLASS", None)
        if custom_response:
            return custom_response(response)
        else:
            return response
api_request = APIRequest




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




