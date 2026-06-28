
from typing import Any, Optional

from .request_utils import RequestUtils
from .request_utils import BASE_API_URL
from .request_utils import EndPoints, PayLoadKeys

import os

class ScribeAPIWrapper:
    def __init__(self, api_key: str, req_timeout: int = 60):
        self._request_utils = RequestUtils()
        self._api_key = api_key
        self._req_timeout = req_timeout
        # Other:
        self._headers = self._request_utils.construct_headers(self._api_key)

    def transcribe(
        self,
        source: str | list[str],
        source_language: str,
        destination_language: str,
        diarization: Optional[str] = None,
    ) -> Any:
        """Send a POST request to the Dadascribe /v1/transcribe
        endpoint and return the parsed response.
    
        Raises InvalidRequestError on failing requests.
        """
        url = BASE_API_URL + EndPoints.TRANSCRIBE
        payload = {
            PayLoadKeys.SOURCE: source,
            PayLoadKeys.SOURCE_LANGUAGE: source_language,
            PayLoadKeys.DEST_LANGUAGE: destination_language,
        }
        if diarization is not None:
            payload[PayLoadKeys.DIARIZATION] = diarization
    
        return self._api_request(url, payload=payload)    
    

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
        output_dir: str,
    ) -> None:
        """Download the transcription output for the given job ID to the specified directory.
        If no directory is specified, saves to the current directory.
        """
        status_info = self.retrieve_status(id)
        if status_info["status"] != "complete":
            raise ValueError("Job is not completed yet. Cannot download output.")

        for file_url in status_info.get("urls", []):
            file_name = os.path.basename(file_url)
            file_content = self._api_request(file_url, get=True)
            with open(os.path.join(output_dir, file_name), "w") as f:
                f.write(file_content)



    def _api_request(
        self,
        url: str,
        payload: Optional[dict] = None,
        get: bool = False
    ) -> Any:
        """Send a POST request to the given URL with the given payload
        and return the parsed response. Higher level version of exec_request
        found in RequestUtils.
    
        Raises InvalidRequestError on failing requests.
        """
        return self._request_utils.exec_request(
            url,
            headers=self._headers,
            payload=payload,
            timeout=self._req_timeout,
            get=get
        )