
from typing import Any, Optional


from .request_utils import RequestUtils
from .request_utils import BASE_API_URL
from .request_utils import EndPoints, PayLoadKeys


class Wrapper:
    def __init__(self, api_key: str, req_timeout: int = 60):
        self._request_utils = RequestUtils()
        self._api_key = api_key
        self._req_timeout = req_timeout
        # Other:
        self._headers = self._request_utils.construct_headers(self._api_key)

    def transcribe(
        self,
        source: str,
        source_language: str,
        destination_language: str,
        diarization: Optional[str] = None,
    ) -> Any:
        """Send a POST request to the Dadascribe /v1/transcribe
        endpoint and return the parsed response.
    
        Raises requests.HTTPError on non-2xx responses.
        """
        url = BASE_API_URL + EndPoints.TRANSCRIBE
        payload = {
            PayLoadKeys.SOURCE: source,
            PayLoadKeys.SOURCE_LANGUAGE: source_language,
            PayLoadKeys.DEST_LANGUAGE: destination_language,
        }
        if diarization is not None:
            payload[PayLoadKeys.DIARIZATION] = diarization
    
        return self._request_utils.exec_request(
            url,
            headers=self._headers,
            payload=payload,
            timeout=self._req_timeout
        )
    
    
    
    def status_request(self, id: str) -> Any:
        """Send a POST request to the Dadascribe /v1/status endpoint
        and return the parsed response.
    
        Raises requests.HTTPError on non-2xx responses.
        """
        url = BASE_API_URL + EndPoints.STATUS
        payload = {PayLoadKeys.ID: id}
    
        return self._request_utils.exec_request(
            url,
            headers=self._headers,
            payload=payload,
            timeout=self._req_timeout
        )
