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

import argparse
import json
import os
import sys
from typing import Any, Optional

import requests


def _exec_request(
    url: str,
    headers: dict,
    payload: dict,
    timeout: int
    = 0
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Call Dadascribe endpoints with requests."
    )
    p.add_argument(
        "--api-key",
        help="Dadascribe API key (or set DADASCRIBE_API_KEY env var).",
    )
    p.add_argument(
        "--source",
        default="https://www.youtube.com/watch?v=VIDEO_ID",
        help="Source media URL (e.g. YouTube link).",
    )
    p.add_argument(
        "--source-language", default="en", help="Source language (e.g. 'en')."
    )
    p.add_argument(
        "--destination-language",
        default="it,fr",
        help="Comma-separated destination languages (e.g. 'it,fr').",
    )
    p.add_argument(
        "--diarization",
        default="Alice,Bob",
        help="Comma-separated diarization labels (e.g. 'Alice,Bob').",
    )
    p.add_argument(
        "--timeout", type=int, default=60, help="Request timeout in seconds."
    )
    p.add_argument(
        "--output",
        help="File to save JSON response (optional). If omitted, prints to stdout.",
    )

    # New argument: check the status of an existing job by ID.
    # If provided, the script will call the /v1/status endpoint instead of
    # submitting a new transcription request.
    p.add_argument(
        "--status-id",
        help="Check status for a previously submitted job ID (e.g. " \
        "a1B2c3D4e5F6g7H8). If provided, transcribe will not run.",
    )

    return p.parse_args()


def main() -> None:
    args = parse_args()
    api_key = args.api_key or os.getenv("DADASCRIBE_API_KEY")
    if not api_key:
        print(
            "Error: API key required. Provide --api-key or set DADASCRIBE_API_KEY env var.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        if args.status_id:
            # If a status ID is provided, perform a status
            # check and ignore other transcribe options.
            result = status_request(
                api_key=api_key, id=args.status_id, timeout=args.timeout
            )
        else:
            result = transcribe(
                api_key=api_key,
                source=args.source,
                source_language=args.source_language,
                destination_language=args.destination_language,
                diarization=args.diarization,
                timeout=args.timeout,
            )
    except Exception as e:
        print(f"Error during request: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved response to {args.output}")
    else:
        # Pretty-print JSON or text
        if isinstance(result, (dict, list)):
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result)


if __name__ == "__main__":
    main()
