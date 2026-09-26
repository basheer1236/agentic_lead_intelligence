import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.errors import (
    HTTPTimeoutError,
    RateLimitError,
    ContentFetchError,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((HTTPTimeoutError, RateLimitError)),
    reraise=True,
)
def fetch_article(url: str) -> str:
    """
    Fetch article HTML with timeout, redirect support, and retry logic for retryable errors.
    """
    try:
        response = httpx.get(
            url,
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        response.raise_for_status()
        return response.text

    except httpx.TimeoutException as exc:
        raise HTTPTimeoutError(f"HTTP Timeout fetching {url}") from exc

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in (429, 502, 503, 504):
            raise RateLimitError(f"HTTP {status} for {url}") from exc
        raise ContentFetchError(f"HTTP {status} fetching {url}") from exc

    except Exception as exc:
        raise ContentFetchError(f"Failed to fetch {url}: {exc}") from exc