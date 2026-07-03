import unittest
from unittest.mock import MagicMock, mock_open, patch

from src.dadascribe.request_utils import (
    BASE_API_URL,
    EndPoints,
    PayLoadKeys,
    ResponseKeys,
    Status,
)
from src.dadascribe.wrapper import DownloadError, ScribeAPIWrapper


class TestWrapper(unittest.TestCase):
    def setUp(self):
        self._wrapper = ScribeAPIWrapper(api_key="")

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_transcribe_calls_api_request_correctly(self, mock_api_request):
        """Checks that the transcribe function calls _api_request
        with the correct arguments, such as the payload."""
        self._wrapper.transcribe(
            source="https://example_source_url.com",
            source_language="en",
            destination_language="it",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "it",
                PayLoadKeys.SOURCE: "https://example_source_url.com",
            },
            file=None,
        )

        mock_api_request.reset_mock()
        # Make sure it works out with diarization as well:
        # Note: "example_source_url" without a protocol is treated as a file
        self._wrapper.transcribe(
            source="example_source_url",
            source_language="en",
            destination_language="it",
            diarization="speaker1,speaker2",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "it",
                PayLoadKeys.DIARIZATION: "speaker1,speaker2",
            },
            file="example_source_url",
        )

        # As a list for the source:
        mock_api_request.reset_mock()
        self._wrapper.transcribe(
            source=["example_source_url", "example_source_url2"],
            source_language="en",
            destination_language="it",
            diarization="speaker1,speaker2",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE: [
                    "example_source_url",
                    "example_source_url2",
                ],
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "it",
                PayLoadKeys.DIARIZATION: "speaker1,speaker2",
            },
            file=None,
        )

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_transcribe_with_file_path(self, mock_api_request):
        """Test that transcribe correctly handles file paths."""
        # Test with a file path (no protocol scheme)
        self._wrapper.transcribe(
            source="/path/to/audio.mp3",
            source_language="en",
            destination_language="fr",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "fr",
            },
            file="/path/to/audio.mp3",
        )

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_transcribe_with_http_url(self, mock_api_request):
        """Test that transcribe correctly handles HTTP URLs."""
        self._wrapper.transcribe(
            source="http://example.com/audio.mp3",
            source_language="en",
            destination_language="es",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "es",
                PayLoadKeys.SOURCE: "http://example.com/audio.mp3",
            },
            file=None,
        )

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_transcribe_with_relative_file_path(self, mock_api_request):
        """Test that transcribe correctly handles relative file paths."""
        self._wrapper.transcribe(
            source="audio_files/recording.wav",
            source_language="de",
            destination_language="en",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE_LANGUAGE: "de",
                PayLoadKeys.DEST_LANGUAGE: "en",
            },
            file="audio_files/recording.wav",
        )

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_transcribe_with_list_of_urls(self, mock_api_request):
        """Test that transcribe handles a list of URLs correctly."""
        self._wrapper.transcribe(
            source=[
                "https://example.com/audio1.mp3",
                "https://example.com/audio2.mp3",
            ],
            source_language="en",
            destination_language="es",
        )
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.TRANSCRIBE,
            payload={
                PayLoadKeys.SOURCE: [
                    "https://example.com/audio1.mp3",
                    "https://example.com/audio2.mp3",
                ],
                PayLoadKeys.SOURCE_LANGUAGE: "en",
                PayLoadKeys.DEST_LANGUAGE: "es",
            },
            file=None,
        )

    @patch("src.dadascribe.wrapper.ScribeAPIWrapper._api_request")
    def test_retrieve_status_calls_api_request_correctly(
        self, mock_api_request
    ):
        """Checks that the retrieve_transcription function calls _api_request
        with the correct arguments, such as the payload."""
        self._wrapper.retrieve_status(id="example_id")
        mock_api_request.assert_called_once()
        mock_api_request.assert_called_with(
            BASE_API_URL + EndPoints.STATUS,
            payload={
                PayLoadKeys.ID: "example_id",
            },
        )

    @patch("os.path.exists")
    def test_download_trsc_raises_err_when_output_dir_dne(self, mock_exists):
        """When the output dir does not exist, should raise DownloadError."""
        mock_exists.return_value = False
        with self.assertRaises(DownloadError):
            self._wrapper.download_transcription_output(
                id="example_id", output_dir="example_path"
            )

    @patch("os.path.exists")
    @patch("src.dadascribe.wrapper.ScribeAPIWrapper.retrieve_status")
    def test_download_trsc_raises_err_when_status_not_complete(
        self, mock_retrieve_status, mock_exists
    ):
        """When the output dir does not exist, should raise DownloadError."""
        mock_exists.return_value = True
        mock_retrieve_status.return_value = {
            ResponseKeys.STATUS: Status.PROCESSING
        }
        with self.assertRaises(DownloadError):
            self._wrapper.download_transcription_output(
                id="example_id", output_dir="example_path"
            )


if __name__ == "__main__":
    unittest.main()
