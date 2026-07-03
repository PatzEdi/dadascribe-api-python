# Stores global constants & utils related to requests.
from enum import StrEnum
from io import BufferedReader
from typing import Optional, Any
from urllib.parse import urlparse
from pathlib import Path
from os import PathLike

import requests
import json

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
    """Raised when a request fails with a non-200 status code.
    Contains the response object for debugging and other useful
    information about the failure."""

    def __init__(self, response: requests.Response):
        self._response = response
        self._message = (
            f"Request failed: {response.status_code} {response.reason}"
        )

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


class InvalidFileError(Exception):
    """Raised when an inputted file is not valid."""

    def __init__(self, message: str):
        self._message = message
        super().__init__(self._message)

    @property
    def message(self) -> str:
        return self._message


class RequestUtils:
    """Utility class for making HTTP requests,
    handling common request logic."""

    def exec_request(
        self,
        api_key: str,
        url: str,
        payload: Optional[dict],
        timeout: int = 0,
        get: bool = False,
        file: Optional[PathLike] | Optional[str] = None
    ) -> str | None:
        """Executes a POST/GET request to the given URL with the given headers
        and payload, and returns the response as JSON or raw text."""
        req_fn = requests.get if get else requests.post
        if file is not None:
            headers = self.construct_headers(api_key, include_content=False)
            payload, file_obj = self.construct_file_payload(file, payload)
            resp = req_fn(
                url,
                headers=headers,
                files=payload, timeout=timeout
            )
            file_obj.close()
        else:
            headers = self.construct_headers(api_key)
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


    def construct_headers(
        self,
        api_key: str,
        include_content: bool = True
    ) -> dict:
        """Contructs a commonly used headers dict with the given API key."""
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        if include_content:
            headers["Content-Type"] = "application/json"
        return headers

    def is_link(self, object: Any) -> bool:
        """Returns whether a given string is a link or not."""
        try:
            stringed = str(object)
            result = urlparse(stringed)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


    def construct_file_payload(
        self,
        file: PathLike | str,
        params: Optional[dict] = None
    ) -> tuple[dict, BufferedReader]:
        """Constructs a file payload dict from the given file path."""
        file = Path(file)
        if not file.is_file():
            raise InvalidFileError(f"File not found or is not a file: {file}")
            
        file_obj = open(file, "rb")
        file_payload = {
            "file": (file.name, file_obj),
            "data": (None, json.dumps(params or {}), "application/json"),
        }
        return file_payload, file_obj