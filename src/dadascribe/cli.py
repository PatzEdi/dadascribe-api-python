
import argparse
import os
import sys
import json

from .internal_globals import ENV_API_NAME
from .wrapper import Wrapper


def _check_api_key_presence(args) -> str:
    api_key = args.api_key or os.getenv(ENV_API_NAME)
    if not api_key:
        print(
            "Error: API key required. Provide --api-key " \
            "or set DADASCRIBE_API_KEY env var.",
            file=sys.stderr,
        )
        sys.exit(2)

    return api_key


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Interact with the DaDaScribe API through the CLI."
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

    p.add_argument(
        "--status-id",
        help="Check status for a previously submitted job ID (e.g. " \
        "a1B2c3D4e5F6g7H8). If provided, transcribe will not run.",
    )

    return p.parse_args()


def _handle_args(args: argparse.Namespace, api_key: str) -> None:
    wrapper = Wrapper(api_key=api_key)
    try:
        if args.status_id:
            # If a status ID is provided, perform a status
            # check and ignore other transcribe options.
            result = wrapper.status_request(
                id=args.status_id, timeout=args.timeout
            )
        else:
            result = wrapper.transcribe(
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



def main() -> None:
    parsed_args = parse_args()
    api_key = _check_api_key_presence(parsed_args)
    _handle_args(parsed_args, api_key)
