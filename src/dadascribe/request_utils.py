
# Stores global constants & utils related to requests.
import requests

from typing import Optional

from enum import StrEnum

BASE_API_URL: str = "https://api.dadascribe.com/v1/"

class EndPoints(StrEnum):
    """Common endpoint names for the API."""
    STATUS = "status"
    TRANSCRIBE = "transcribe"


class PayLoadKeys(StrEnum):
    """Common payload keys for the API."""
    ID = "id"
    SOURCE = "source"
    SOURCE_LANGUAGE = "source-language"
    DEST_LANGUAGE = "destination-language"
    DIARIZATION = "diarization"


class ResponseKeys(StrEnum):
    """Common response keys for the API."""
    STATUS = "status"
    URLS = "urls"


class Status(StrEnum):
    """Common status values for the API."""
    COMPLETE = "complete"
    PROCESSING = "processing"
    ERROR = "error"


def extract_response_content(resp: requests.Response) -> str:
    """Helper to extract the response content as JSON or raw text."""
    try:
        return resp.json()
    except ValueError:
        return resp.text


class InternalRequestError(Exception):
    def __init__(self, response: requests.Response):
        self._response = response
        self._message = f"Request failed: {response.status_code} " \
                    f"{response.reason}"

        super().__init__(self.message)

    @property
    def response(self) -> requests.Response:
        return self._response
    
    @property
    def message(self) -> str:
        return self._message

    @property
    def resp_body(self) -> str:
        return extract_response_content(self._response)


class RequestUtils:
    
    def exec_request(
        self,
        url: str,
        headers: Optional[dict],
        payload: Optional[dict],
        timeout: int = 0,
        get: bool = False
    ) -> str | None:
        """Executes a POST request to the given URL with the given headers and
        payload, and returns the response as JSON or raw text."""
        req_fn = requests.get if get else requests.post
        resp = req_fn(
            url,
            headers=headers,
            json=payload, timeout=timeout
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            raise InternalRequestError(resp)
    
        # Return JSON if possible, otherwise raw text
        return extract_response_content(resp)


    def construct_headers(self, api_key: str) -> dict:
        """Contructs a commonly used headers dict with the given API key."""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }