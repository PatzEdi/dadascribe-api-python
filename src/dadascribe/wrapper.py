import os
from os import PathLike
from typing import Any, Optional

from .request_utils import (
    BASE_API_URL,
    EndPoints,
    PayLoadKeys,
    RequestUtils,
    ResponseKeys,
    Status,
)


class DownloadError(Exception):
    """Raised when download fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ScribeAPIWrapper:
    def __init__(self, api_key: str, req_timeout: int = 60):
        self._request_utils = RequestUtils()
        self._api_key = api_key
        self._req_timeout = req_timeout

    def transcribe(
        self,
        source: str | list[str] | PathLike,
        source_language: str,
        destination_language: str,
        diarization: Optional[str] = None,
    ) -> Any:
        """Send a POST request to the Dadascribe /v1/transcribe
        endpoint and return the parsed response.

        Raises InvalidRequestError on failing requests.
        """
        url = BASE_API_URL + EndPoints.TRANSCRIBE
        payload: dict[str, Any] = {
            PayLoadKeys.SOURCE_LANGUAGE: source_language,
            PayLoadKeys.DEST_LANGUAGE: destination_language,
        }
        if diarization is not None:
            payload[PayLoadKeys.DIARIZATION] = diarization
        file_source = None
        if isinstance(source, list) or self._request_utils.is_link(source):
            print("Source detected as LINK or LIST of LINKS.")
            payload[PayLoadKeys.SOURCE] = source
        else:
            print("Source detected as FILE.")
            # Construct files data:
            file_source = source

        return self._api_request(url, payload=payload, file=file_source)

    def retrieve_status(self, id: str) -> Any:
        """Send a POST request to the Dadascribe /v1/status endpoint
        and return the parsed response.

        Raises InvalidRequestError on failing requests.
        """
        url = BASE_API_URL + EndPoints.STATUS
        payload = {PayLoadKeys.ID: id}

        return self._api_request(url, payload=payload)

    def download_transcription_output(
        self,
        id: str,
        output_dir: str | PathLike,
    ) -> None:
        """Download the transcription output for the given job ID
        to the specified directory. If no directory is specified,
        saves to the current directory.
        """
        if not os.path.exists(output_dir):
            raise DownloadError(
                f'Output directory "{output_dir}" does not exist.'
            )

        status_info = self.retrieve_status(id)
        if status_info[ResponseKeys.STATUS] != Status.COMPLETE:
            raise DownloadError(
                "Job is not completed yet. Cannot download output."
            )

        for file_url in status_info.get(ResponseKeys.URLS, []):
            file_name = os.path.basename(file_url)
            file_content = self._api_request(file_url, get=True)
            with open(os.path.join(output_dir, file_name), "w") as f:
                f.write(file_content)

    def _api_request(
        self,
        url: str,
        payload: Optional[dict] = None,
        get: bool = False,
        file: Optional[Any] = None,
    ) -> Any:
        """Send a POST request to the given URL with the given payload
        and return the parsed response. Higher level version of exec_request
        found in RequestUtils.

        Raises InvalidRequestError on failing requests.
        """
        return self._request_utils.exec_request(
            self._api_key,
            url,
            payload=payload,
            timeout=self._req_timeout,
            get=get,
            file=file,
        )
