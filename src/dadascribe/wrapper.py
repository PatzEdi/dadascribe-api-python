
from typing import Any, Optional


from .request_utils import RequestUtils


class Wrapper:
    def __init__(self, api_key: str):
        self._request_utils = RequestUtils()
        self._api_key = api_key

    def transcribe(
        self,
        source: str,
        source_language: str,
        destination_language: str,
        diarization: Optional[str] = None,
        timeout: int = 60,
    ) -> Any:
        """Send a POST request to the Dadascribe /v1/transcribe endpoint and return the parsed response.
    
        Raises requests.HTTPError on non-2xx responses.
        """
        url = "https://api.dadascribe.com/v1/transcribe"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "source": source,
            "source-language": source_language,
            "destination-language": destination_language,
        }
        if diarization is not None:
            payload["diarization"] = diarization
    
        return self._request_utils.exec_request(url, headers=headers, payload=payload, timeout=timeout)
    
    
    
    def status_request(self, id: str, timeout: int = 60) -> Any:
        """Send a POST request to the Dadascribe /v1/status endpoint with a job ID and return the parsed response.
    
        Mirrors:
        curl -sS -X POST 'https://api.dadascribe.com/v1/status' \
        -H 'Authorization: Bearer YOUR_API_KEY' \
        -H 'Content-Type: application/json' \
        -d '{ "id": "a1B2c3D4e5F6g7H8" }'
        """
        url = "https://api.dadascribe.com/v1/status"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {"id": id}
        return self._request_utils.exec_request(url, headers=headers, payload=payload, timeout=timeout)
