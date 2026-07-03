
import argparse
import os
import sys
import json

from .internal_globals import ENV_API_NAME
from .wrapper import ScribeAPIWrapper, DownloadError
from .request_utils import InternalRequestError, InvalidFileError


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
        help="Source media URL (e.g. YouTube link) OR file path.",
    )
    p.add_argument(
        "--source-language", default="en", help="Source language (e.g. 'en')."
    )
    p.add_argument(
        "--destination-language",
        default="",
        help="Comma-separated destination languages (e.g. 'it,fr').",
    )
    p.add_argument(
        "--diarization",
        default="",
        help="Comma-separated diarization labels (e.g. 'Alice,Bob').",
    )
    p.add_argument(
        "--timeout", type=int, default=60, help="Request timeout in seconds."
    )
    p.add_argument(
        "--dump-response",
        help="File to save JSON response (optional). "
            "If omitted, prints to stdout.",
    )

    p.add_argument(
        "--status-id",
        help="Check status for a previously submitted job ID (e.g. " \
        "a1B2c3D4e5F6g7H8). If provided, transcribe will not run.",
    )

    # For downloading transcription files:

    p.add_argument(
        "--download",
        help="Download generated files given a job ID " \
            "& an optional output dir path" \
    )

    p.add_argument(
        "--download-output-dir",
        default=None,
        help="Directory to save downloaded files (optional). " \
            "If omitted, saves to current directory."
    )
    
    return p.parse_args()


def _handle_args(args: argparse.Namespace, api_key: str) -> None:
    wrapper = ScribeAPIWrapper(api_key=api_key, req_timeout=args.timeout)
    try:
        if args.status_id:
            # If a status ID is provided, perform a status
            # check and ignore other transcribe options.
            result = wrapper.retrieve_status(id=args.status_id)
        elif args.download:
            result = wrapper.download_transcription_output(
                id=args.download,
                output_dir=args.download_output_dir or os.getcwd(),
            )
        else:
            result = wrapper.transcribe(
                source=args.source,
                source_language=args.source_language,
                destination_language=args.destination_language,
                diarization=args.diarization,
            )
    except (InternalRequestError, InvalidFileError, DownloadError) as e:
        if isinstance(e, DownloadError) or isinstance(e, InvalidFileError):
            print(f"Error: {e.message}", file=sys.stderr)
        elif isinstance(e, InternalRequestError):
            print(f"Error during request: {e.resp_body}", file=sys.stderr)

        sys.exit(1)

    if args.dump_response:
        with open(args.dump_response, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved response to {args.dump_response}")
    else:
        # Pretty-print JSON or text
        if isinstance(result, (dict, list)):
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif result is not None:
            print(result)



def main() -> None:
    parsed_args = parse_args()
    api_key = _check_api_key_presence(parsed_args)
    _handle_args(parsed_args, api_key)
