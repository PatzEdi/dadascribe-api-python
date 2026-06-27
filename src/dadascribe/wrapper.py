#!/usr/bin/env python3
"""
api_test.py

Example using requests to POST to the Dadascribe transcription API.

Usage:
  - Set environment variable `DADASCRIBE_API_KEY` to your API key, or pass `--api-key`.
  - Run transcription (defaults mirror the original curl):
      python api_test.py
  - Check status of a previously submitted job by ID:
      python api_test.py --status-id a1B2c3D4e5F6g7H8

  - To override params:
      python api_test.py --source "https://youtu.be/VIDEO_ID" --destination-language "it,fr" --diarization "Alice,Bob"
"""

import json
import sys
from typing import Any, Optional

import requests


def _exec_request(
    url: str,
    headers: dict,
    payload: dict,
    timeout: int = 0
) -> str | None:
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        # Print details for easier debugging, then re-raise
        print(
            f"Request failed: {resp.status_code} {resp.reason}",
            file=sys.stderr,
        )
        try:
            print(
                json.dumps(resp.json(), indent=2, ensure_ascii=False),
                file=sys.stderr,
            )
        except ValueError:
            print(resp.text, file=sys.stderr)
        raise

    # Return JSON if possible, otherwise raw text
    try:
        return resp.json()
    except ValueError:
        return resp.text



def transcribe(
    api_key: str,
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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "source": source,
        "source-language": source_language,
        "destination-language": destination_language,
    }
    if diarization is not None:
        payload["diarization"] = diarization

    return _exec_request(url, headers=headers, payload=payload, timeout=timeout)



def status_request(api_key: str, id: str, timeout: int = 60) -> Any:
    """Send a POST request to the Dadascribe /v1/status endpoint with a job ID and return the parsed response.

    Mirrors:
    curl -sS -X POST 'https://api.dadascribe.com/v1/status' \
      -H 'Authorization: Bearer YOUR_API_KEY' \
      -H 'Content-Type: application/json' \
      -d '{ "id": "a1B2c3D4e5F6g7H8" }'
    """
    url = "https://api.dadascribe.com/v1/status"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"id": id}
    return _exec_request(url, headers=headers, payload=payload, timeout=timeout)
