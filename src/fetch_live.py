"""Generic adapter skeleton, not a verified iSolarCloud API contract."""

import os
from urllib.parse import urlsplit
import requests
from dotenv import load_dotenv


def fetch_raw(http=requests):
    load_dotenv()
    url, token = os.getenv("SUNGROW_API_URL"), os.getenv("SUNGROW_API_TOKEN")
    if not url or not token:
        raise ValueError("Configure SUNGROW_API_URL and SUNGROW_API_TOKEN")
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Use an HTTPS endpoint without embedded credentials")
    try:
        response = http.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
            allow_redirects=False,
        )
        response.raise_for_status()
        if 300 <= response.status_code < 400:
            raise ValueError("Redirect refused")
        return response.json()
    except (requests.RequestException, ValueError):
        raise RuntimeError(
            "API request failed; verify configuration and vendor contract"
        ) from None
