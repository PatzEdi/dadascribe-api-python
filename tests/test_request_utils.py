import unittest
from unittest.mock import patch, mock_open

import requests
from src.dadascribe.request_utils import (
    InternalRequestError,
    InvalidFileError,
    RequestUtils,
    extract_response_content,
)


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
        resp._content = b"response as a string"
        result = extract_response_content(resp)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "response as a string")

    def test_construct_headers(self):
        """Makes sure that the headers we construct
        are of the expected form. This is more of a confirmation
        that we want to change this header format in the code."""
        headers = self._request_utils.construct_headers("dummy_api_key")
        self.assertIsInstance(headers, dict)
        self.assertEqual(
            headers,
            {
                "Authorization": "Bearer dummy_api_key",
                "Content-Type": "application/json",
            },
        )

        # Now excluding content type:
        headers = self._request_utils.construct_headers(
            "dummy_api_key",
            include_content=False
        )
        self.assertIsInstance(headers, dict)
        self.assertEqual(
            headers,
            {
                "Authorization": "Bearer dummy_api_key"
            },
        )

    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_calls_post_correctly(self, mock_post):
        resp = mock_post.return_value
        resp._content = b'{"dummy": "response"}'
        resp.status_code = 200
        self._request_utils.exec_request(
            "dummy_api_key", "https://dummy.url", {}
        )
        mock_post.assert_called_once()
        mock_post.assert_called_with(
            "https://dummy.url",
            headers={
                "Authorization": "Bearer dummy_api_key",
                "Content-Type": "application/json",
            },
            json={},
            timeout=0,
        )

    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_raises_internal_request_error_on_status_raised(
        self, mock_post
    ):
        resp = mock_post.return_value
        resp.status_code = 500
        resp.reason = "Bad Request"
        with self.assertRaises(InternalRequestError) as context:
            self._request_utils.exec_request(
                "dummy_api_key", "https://dummy.url", {}
            )
        self.assertEqual(
            str(context.exception), "Request failed: 500 Bad Request"
        )

    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_returns_formatted_extraction_content_output(
        self, mock_post
    ):
        resp = mock_post.return_value
        resp._content = b'["response", "content", "as", "list"]'
        resp.status_code = 200
        result = self._request_utils.exec_request(
            "dummy_api_key", "https://dummy.url", {}
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["response", "content", "as", "list"])

    def test_is_link(self):
        """Test is_link correctly identifies URLs and non-URLs."""
        # Valid URLs
        self.assertTrue(self._request_utils.is_link("https://example.com"))
        self.assertTrue(self._request_utils.is_link("http://example.com"))
        self.assertTrue(
            self._request_utils.is_link("https://example.com/path/to/file.mp3")
        )
        self.assertTrue(self._request_utils.is_link("ftp://example.com"))

        # Not valid URLs (no scheme or no netloc)
        self.assertFalse(self._request_utils.is_link("example.com"))
        self.assertFalse(self._request_utils.is_link("/path/to/file.mp3"))
        self.assertFalse(self._request_utils.is_link("file.mp3"))
        self.assertFalse(self._request_utils.is_link("just_a_string"))
        self.assertFalse(self._request_utils.is_link(""))

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=b"file content",
    )
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("requests.post", return_value=requests.Response())
    def test_exec_request_with_file(
        self, mock_post, mock_exists, mock_is_file, mock_open_file
    ):
        """Test that exec_request correctly handles file uploads."""
        resp = mock_post.return_value
        resp._content = b'{"id": "test_id"}'
        resp.status_code = 200

        result = self._request_utils.exec_request(
            "dummy_api_key",
            "https://dummy.url",
            {"key": "value"},
            file="/path/to/test.mp3",
        )

        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Verify headers don't include Content-Type (multipart/form-data is automatic)
        self.assertEqual(
            call_args.kwargs["headers"],
            {"Authorization": "Bearer dummy_api_key"},
        )

        # Verify files parameter is present
        self.assertIn("files", call_args.kwargs)
        self.assertEqual(result, {"id": "test_id"})

    @patch("pathlib.Path.is_file", return_value=False)
    def test_construct_file_payload_raises_on_non_file(
        self, mock_is_file
    ):
        """Test that construct_file_payload raises InvalidFileError for non-files."""
        with self.assertRaises(InvalidFileError) as context:
            self._request_utils.construct_file_payload("/path/to/directory")
        self.assertIn(
            "File not found or is not a file", str(context.exception)
        )

    def test_construct_headers_with_include_content_false(self):
        """Test construct_headers without Content-Type for file uploads."""
        headers = self._request_utils.construct_headers(
            "dummy_api_key", include_content=False
        )
        self.assertIsInstance(headers, dict)
        self.assertEqual(
            headers,
            {"Authorization": "Bearer dummy_api_key"},
        )
        self.assertNotIn("Content-Type", headers)


if __name__ == "__main__":
    unittest.main()
