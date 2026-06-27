
# Stores global constants & utils related to requests.
import requests
import sys
import json

BASE_API_URL: str = "https://api.dadascribe.com/v1/"

class RequestUtils:
    
    def exec_request(
        self,
        url: str,
        headers: dict,
        payload: dict,
        timeout: int = 0
    ) -> str | None:
        """Executes a POST request to the given URL with the given headers and
        payload, and returns the response as JSON or raw text."""
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


    def construct_headers(self, api_key: str) -> dict:
        """Contructs a commonly used headers dict with the given API key."""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }