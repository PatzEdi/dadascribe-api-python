import unittest
from unittest.mock import patch

from src.dadascribe.request_utils import BASE_API_URL, EndPoints, PayLoadKeys
from src.dadascribe.request_utils import ResponseKeys, Status
from src.dadascribe.wrapper import ScribeAPIWrapper, DownloadError


class TestWrapper(unittest.TestCase):
    def setUp(self):
        self._wrapper = ScribeAPIWrapper(api_key="")

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_transcribe_calls_api_request_correctly(self, mock_api_request):
        """Checks that the transcribe function calls _api_request
        with the correct arguments, such as the payload."""
        self._wrapper.transcribe(
            source="example_source_url",
            source_language="en",
            destination_language="it",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE: "example_source_url",
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "it",
            },
        )

        mock_api_request.reset_mock()
        # Make sure it works out with diarization as well:
        self._wrapper.transcribe(
            source="example_source_url",
            source_language="en",
            destination_language="it",
            diarization="speaker1,speaker2"
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE: "example_source_url",
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "it",
                PayLoadKeys.DIARIZATION: "speaker1,speaker2",
            },
        )

        # As a list for the source:
        mock_api_request.reset_mock()
        self._wrapper.transcribe(
            source=["example_source_url", "example_source_url2"],
            source_language="en",
            destination_language="it",
            diarization="speaker1,speaker2"
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE: [
                    "example_source_url",
                    "example_source_url2"
                ],
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "it",
                PayLoadKeys.DIARIZATION: "speaker1,speaker2",
            },
        )

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_retrieve_status_calls_api_request_correctly(
        self,
        mock_api_request
    ):
        """Checks that the retrieve_transcription function calls _api_request
        with the correct arguments, such as the payload."""
        self._wrapper.retrieve_status(id="example_id")
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.STATUS,
            payload={
                PayLoadKeys.ID: "example_id",
            }
        )


    @patch("os.path.exists")
    def test_download_trsc_raises_err_when_output_dir_dne(self, mock_exists):
        """When the output dir does not exist, should raise DownloadError."""
        mock_exists.return_value = False
        with self.assertRaises(DownloadError):
            self._wrapper.download_transcription_output(
                id="example_id",
                output_dir="example_path"
            )

    @patch("os.path.exists")
    @patch("src.dadascribe.wrapper.ScribeAPIWrapper.retrieve_status")
    def test_download_trsc_raises_err_when_status_not_complete(
        self,
        mock_retrieve_status,
        mock_exists
    ):
        """When the output dir does not exist, should raise DownloadError."""
        mock_exists.return_value = True
        mock_retrieve_status.return_value = {
            ResponseKeys.STATUS:
                Status.PROCESSING
        }
        with self.assertRaises(DownloadError):
            self._wrapper.download_transcription_output(
                id="example_id",
                output_dir="example_path"
            )
        

if __name__ == "__main__":
    unittest.main()
