# apyclient.py
# A python client api library.
# Copyright (C) 2012 Aaron Madison

# Released subject to the BSD License


__all__ = (
    'api_request',
    'SignedAPIRequest',
    'BaseResponse',
    'JSONApiResponse',
)

__version__ = "0.0.2"

from functools import wraps
import json
import socket
from urllib import urlencode
import urllib2
from urlparse import parse_qs

import apysigner

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



class SignedAPIRequest(APIRequest):
    """
    Signs an API request.

    You can subclass this and then use that as your decorator.
    class MySignedAPI(SignedAPIRequest):
        CLIENT_ID = "client-id"
        PRIVATE_KEY = "UHJpdmF0ZSBLZXk="

    signed_request = MySignedAPI

    @signed_request('/something/good', method='POST')
    def post_something():
        return {'good_thing': 'babies'}
    """
    CLIENT_PARAM_NAME = 'ClientId'
    SIGNATURE_PARAM_NAME = 'Signature'

    CLIENT_ID = ''
    PRIVATE_KEY = ''

    def _open_url(self, url, query_data):
        """
        Don't sign until last step before opening url
        """
        url = self._get_signed_url(url, query_data)
        return urllib2.urlopen(url, data=query_data, timeout=self.timeout)

    def _get_signed_url(self, url, query_data):
        # Currently limited to kinds of data that are key=value pairs.
        # Binary data is not supported.
        url_with_client = self._get_url_with_client(url)
        payload = query_data and parse_qs(query_data)
        signature = apysigner.get_signature(self.PRIVATE_KEY, url_with_client, payload)
        return url_with_client + "&{0}={1}".format(self.SIGNATURE_PARAM_NAME, signature)

    def _get_url_with_client(self, url):
        url_conjunction = "&" if "?" in url else "?"
        return url + "{url_conj}{param_name}={client_id}".format(
            url_conj=url_conjunction,
            param_name=self.CLIENT_PARAM_NAME,
            client_id=self.CLIENT_ID,
        )


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




