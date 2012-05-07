
from cStringIO import StringIO
import json
import mock
from unittest import TestCase, main
import urllib2


import apyclient

__all__ = (
    'BaseResponseTests',
    'ApiRequestTests',
    'SignedAPIRequestTests',
    'JSONApiResponseTests',
)

class CustomResponse(object):
    def __init__(self, response):
        self._response = response

class CustomResponseTwo(object):
    def __init__(self, response):
        self._response = response

class ResponseStub(object):

    def __init__(self, code=None, msg=None, content=None):
        self.code = code
        self.msg = msg
        self.content = content

    def read(self):
        return self.content


class TestSignedRequest(apyclient.SignedAPIRequest):
    CLIENT_ID = "client-test"
    PRIVATE_KEY = "UHJpdmF0ZSBLZXk="
test_signed_request = TestSignedRequest

class ApiStub(object):
    HOST_NAME = "http://www.example.com"

    @apyclient.api_request("/do-something/", timeout=10)
    def do_something(self):
        return {'times': 5}

    @apyclient.api_request("/do-simple/", timeout=10)
    def do_simple(self):
        pass

    @apyclient.api_request("/do-multiple/", timeout=3)
    def do_multiple(self):
        return {'times': [5, 3]}

    @apyclient.api_request("/do-post/", method="POST", timeout=30)
    def do_post(self):
        return {
            'one_thing': "this&that",
            'other_thing': "a/path"
        }


class ApiCustomResponseStub(ApiStub):
    RESPONSE_CLASS = CustomResponseTwo

    @apyclient.api_request("/do-custom/", response_class=CustomResponse)
    def do_custom(self):
        return {}


class BaseResponseTests(TestCase):

    def test_status_code(self):
        r = ResponseStub(code=200)
        response = apyclient.BaseResponse(r)
        self.assertEqual(200, response.code)

    def test_is_success(self):
        r = ResponseStub(code=200)
        response = apyclient.BaseResponse(r)
        self.assertEqual(True, response.is_success)

    def test_not_success(self):
        redirect = apyclient.BaseResponse(ResponseStub(code=301))
        bad_request = apyclient.BaseResponse(ResponseStub(code=400))
        server_error = apyclient.BaseResponse(ResponseStub(code=500))

        self.assertEqual(False, redirect.is_success)
        self.assertEqual(False, bad_request.is_success)
        self.assertEqual(False, server_error.is_success)

    def test_returns_content(self):
        raw = ResponseStub(code=200, content="This is my content")
        response = apyclient.BaseResponse(raw)

        self.assertEqual(raw.content, response.content)

    def test_caches_response_content(self):
        raw = ResponseStub(code=200, content="This is my content")
        response = apyclient.BaseResponse(raw)

        with mock.patch.object(raw, 'read') as read:
            c = response.content
            c2 = response.content

        self.assertEqual(1, read.call_count)
        self.assertEqual(c2, c)


class ApiRequestTests(TestCase):

    @mock.patch("urllib2.urlopen")
    def test_calls_urlopen_with_full_get_url(self, urlopen):
        api = ApiStub()
        api.do_something()
        urlopen.assert_called_once_with("http://www.example.com/do-something/?times=5", data=None, timeout=10)

    @mock.patch("urllib2.urlopen")
    def test_allows_sequence_for_data_args(self, urlopen):
        api = ApiStub()
        api.do_multiple()
        urlopen.assert_called_once_with("http://www.example.com/do-multiple/?times=5&times=3", data=None, timeout=3)

    @mock.patch("urllib2.urlopen")
    def test_calls_urlopen_with_post_content(self, urlopen):
        api = ApiStub()
        api.do_post()

        urlopen.assert_called_once_with("http://www.example.com/do-post/",
            data="one_thing=this%26that&other_thing=a%2Fpath", # url encoded
            timeout=30,
        )

    @mock.patch("urllib2.urlopen")
    def test_makes_correct_call_when_no_data_to_pass(self, urlopen):
        api = ApiStub()
        api.do_simple()

        urlopen.assert_called_once_with("http://www.example.com/do-simple/",
            data=None,
            timeout=10,
        )

    @mock.patch("urllib2.urlopen")
    def test_returns_response_when_successful_response(self, urlopen):
        resp = urllib2.addinfourl(StringIO("mock_content"), "mock headers", url="http://www.example.com/", code="200")
        urlopen.return_value = resp

        api_stub = ApiStub()
        response = api_stub.do_something()
        self.assertEqual(resp, response)

    @mock.patch("urllib2.urlopen")
    def test_returns_http_error(self, urlopen):
        err = urllib2.HTTPError(url="http://www.example.com/", code="403", msg="Permission Denied", hdrs="mock headers", fp=StringIO("mock_content"))
        urlopen.side_effect = err

        api_stub = ApiStub()
        response = api_stub.do_something()
        self.assertEqual(err, response)

    @mock.patch("urllib2.urlopen")
    def test_returns_custom_response_class_when_declared_on_method(self, urlopen):
        resp = urllib2.addinfourl(StringIO("mock_content"), "mock headers", url="http://www.example.com/", code="200")
        urlopen.return_value = resp

        api_stub = ApiCustomResponseStub()
        response = api_stub.do_custom()
        self.assertIsInstance(response, CustomResponse)
        self.assertEqual(resp, response._response)

    @mock.patch("urllib2.urlopen")
    def test_returns_custom_response_class_when_declared_on_api_class(self, urlopen):
        resp = urllib2.addinfourl(StringIO("mock_content"), "mock headers", url="http://www.example.com/", code="200")
        urlopen.return_value = resp

        api_stub = ApiCustomResponseStub()
        response = api_stub.do_something()
        self.assertIsInstance(response, CustomResponseTwo)
        self.assertEqual(resp, response._response)





class SignedAPIRequestTests(TestCase):

    def test_subclasses_api_request(self):
        self.assertTrue(issubclass(apyclient.SignedAPIRequest, apyclient.APIRequest))

    @mock.patch("apysigner.get_signature")
    def test_adds_client_param_name_and_value_to_url_before_sending_to_get_signature(self, get_signature):
        endpoint = "/do_this/"
        url = endpoint + "?thing=clap"
        sut = TestSignedRequest(endpoint)
        sut._get_signed_url(url, None)

        expected_url_to_sign = url + "&{0}={1}".format(sut.CLIENT_PARAM_NAME, sut.CLIENT_ID)
        get_signature.assert_called_once_with(sut.PRIVATE_KEY, expected_url_to_sign, None)

    @mock.patch("apysigner.get_signature")
    def test_adds_client_info_when_no_existing_get_data(self, get_signature):
        endpoint = "/do_this/"
        sut = TestSignedRequest(endpoint)
        sut._get_signed_url(endpoint, None)

        expected_url_to_sign = endpoint + "?{0}={1}".format(sut.CLIENT_PARAM_NAME, sut.CLIENT_ID)
        get_signature.assert_called_once_with(sut.PRIVATE_KEY, expected_url_to_sign, None)

    @mock.patch("apysigner.get_signature")
    def test_adds_client_info_when_post_request(self, get_signature):
        endpoint = "/do_this/"
        post_data = 'thing=clap'
        sut = TestSignedRequest(endpoint)
        sut._get_signed_url(endpoint, post_data)

        expected_url_to_sign = endpoint + "?{0}={1}".format(sut.CLIENT_PARAM_NAME, sut.CLIENT_ID)
        get_signature.assert_called_once_with(sut.PRIVATE_KEY, expected_url_to_sign, {'thing': ['clap']})

    def test_returns_url_with_signature_attached(self):
        endpoint = "/do_this/"
        sut = TestSignedRequest(endpoint)

        signed_url = sut._get_signed_url(endpoint, None)

        expected_url = endpoint + "?{client}={client_id}&{sig}={signature}".format(
            client=sut.CLIENT_PARAM_NAME,
            client_id=sut.CLIENT_ID,
            sig=sut.SIGNATURE_PARAM_NAME,
            signature='IF5ygqTozyktR9dEWhf-DR9sICI1dyDEea6PMtuTRxA='
        )
        self.assertEqual(expected_url, signed_url)

    @mock.patch("urllib2.urlopen")
    def test_sends_signed_request_to_url_opener(self, urlopen):
        endpoint = "/do_this/"
        query_data = "thing=clap"
        sut = TestSignedRequest(endpoint)

        sut._open_url(endpoint, query_data)
        expected_url = endpoint + "?{client}={client_id}&{sig}={signature}".format(
            client=sut.CLIENT_PARAM_NAME,
            client_id=sut.CLIENT_ID,
            sig=sut.SIGNATURE_PARAM_NAME,
            signature='K3oNp0dyUcIth1NfLthRpauBINDMo-ycddb-bcvpkJo='
        )
        urlopen.assert_called_once_with(expected_url, data=query_data, timeout=sut.timeout)

class JSONApiResponseTests(TestCase):

    def get_data(self):
        return {"this": "is_test_data", "and_also": ["something", 12, "complicated"]}

    def test_loads_json_from_content(self):
        data = self.get_data()
        raw = ResponseStub(code=200, content=json.dumps(data))
        response = apyclient.JSONApiResponse(raw)

        self.assertEqual(data, response.json())

    def test_caches_json_response(self):
        data = self.get_data()
        raw = ResponseStub(code=200, content=json.dumps(data))
        response = apyclient.JSONApiResponse(raw)

        with mock.patch('json.loads') as load:
            load.return_value = data
            one = response.json()
            two = response.json()
        self.assertEqual(two, one)
        self.assertEqual(1, load.call_count)




if __name__ == '__main__':
    main()

