apyclient
=========

A Python API Client

Overview
--------

Allows you to easily create client APIs in a highly customizable way.


Installation
------------
Only requirement is python 2.6 or greater. Tests require 'mock' package.

::

    pip install apyclient


Usage
-----

You are able to easily create a client Api class. The only requirement of
the API class is that it must have a "HOST_NAME" attribute declared. The API
uses this host name to prepend to the endpoint when building the request.

::

    class MyAPIClient(object):
        HOST_NAME = "http://www.example.com"

        @api_request("/api-endpoint/")
        def fetch_some_stuff(some_var):
            return {"the_variable": some_var}

    my_client = MyApiClient()
    my_client.fetch_some_stuff(3)

And that's it. The client will make an HTTP GET request by default with the
data provided by the decorated method.

You can also do a POST request by declaring ``method="POST"`` in the api_request.

::

        @api_request("/api-endpoint/", method="POST")
        def fetch_some_stuff(some_var):
            return {"the_variable": some_var}


And finally, you are able to return a custom response class if you so desire.
Just either provide a ``RESPONSE_CLASS`` on the api client class, or a
``response_class`` on the api_request decorator. If you have a custom response
class declared both on the API client and on the api_request decorator, the
decorator will win because it is more specific. The response class must take
one argument on initialization, the original response.

::

    class MyApiClient(object):
        HOST_NAME = "http://www.example.com/api
        RESPONSE_CLASS = MyDefaultResponseClass

        @api_request("/api-endpoint/")
        def fetch_some_stuff(some_var):
            return {"the_variable": some_var}

        @api_request("/api-endpoint/", response_class=SpecializedResponseClass)
        def fetch_some_stuff(some_var):
            return {"the_variable": some_var}
