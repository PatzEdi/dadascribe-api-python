import unittest
from unittest.mock import patch

import requests

from src.dadascribe.request_utils import extract_response_content
from src.dadascribe.request_utils import RequestUtils
from src.dadascribe.request_utils import InternalRequestError

class TestRequestUtils(unittest.TestCase):
    def setUp(self):
        self._request_utils = RequestUtils()

    def test_extract_response_content(self):
        resp = requests.Response()
        resp._content = b'{"key": "value"}'
        result = extract_response_content(resp)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"key": "value"})

        # Now with a list:
        resp._content = b'["response", "content", "as", "list"]'
        result = extract_response_content(resp)
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["response", "content", "as", "list"])

        # Now with a string:
        resp._content = b'response as a string'
        result = extract_response_content(resp)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "response as a string")


    def test_construct_headers(self):
        """Makes sure that the headers we construct
        are of the expected form. This is more of a confirmation
        that we want to change this header format in the code."""
        headers = self._request_utils.construct_headers("dummy_api_key")
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers,
            {
                "Authorization": "Bearer dummy_api_key",
                "Content-Type": "application/json",
            }
        )

    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_calls_post_correctly(self, mock_post):
        resp = mock_post.return_value
        resp._content = b'{"dummy": "response"}'
        resp.status_code = 200
        self._request_utils.exec_request("https://dummy.url", {}, {})
        mock_post.assert_called_once()
        mock_post.assert_called_with("https://dummy.url", headers={}, json={}, timeout=0)


    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_raises_internal_request_error_on_status_raised(self, mock_post):
        resp = mock_post.return_value
        resp.status_code = 500
        resp.reason = "Bad Request"
        with self.assertRaises(InternalRequestError) as context:
            self._request_utils.exec_request("https://dummy.url", {}, {})
        self.assertEqual(str(context.exception), "Request failed: 500 Bad Request")


    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_returns_formatted_extraction_content_output(self, mock_post):
        resp = mock_post.return_value
        resp._content = b'["response", "content", "as", "list"]'
        resp.status_code = 200
        result = self._request_utils.exec_request("https://dummy.url", {}, {})
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["response", "content", "as", "list"])


if __name__ == "__main__":
    unittest.main()
