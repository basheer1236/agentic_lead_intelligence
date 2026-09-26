"""
Pre-tool guardrails for deterministic validation of tool invocations.
Enforces URL validation, public-source policies, allowed tool registries, and execution budgets.
"""

from urllib.parse import urlparse
from app.config.settings import settings
from app.errors import StateValidationError


ALLOWED_TOOLS = {
    "rss_fetcher",
    "article_filter",
    "article_dedup",
    "http_fetcher",
    "html_parser",
    "ad_directory_scraper",
    "ad_search_scraper",
    "designer_profile_scraper",
    "tavily_public_search",
    "public_source_fetcher",
    "website_fetcher",
    "designer_resolver",
    "postgresql_persistence",
}


def validate_public_url(url: str) -> None:
    """Enforce HTTP/HTTPS public URL safety rules."""
    if not url or not isinstance(url, str):
        raise StateValidationError("URL must be a non-empty string.")

    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise StateValidationError(f"Invalid URL scheme '{parsed.scheme}'. Only http/https are allowed.")

    if not parsed.netloc or not parsed.hostname:
        raise StateValidationError("Invalid URL: missing domain host.")

    host = parsed.hostname.lower()
    if host in ("localhost", "127.0.0.1", "0.0.0.0") or host.startswith("192.168.") or host.startswith("10."):
        raise StateValidationError(f"Access to private/internal network host '{host}' is prohibited.")


def check_tool_allowed(tool_name: str) -> None:
    """Enforce tool registration guardrail."""
    if tool_name not in ALLOWED_TOOLS:
        raise StateValidationError(f"Tool '{tool_name}' is not in the allowed tool registry.")


def check_call_budget(current_calls: int) -> None:
    """Enforce maximum LLM / tool call limit guardrail per article."""
    max_calls = getattr(settings, "max_llm_calls_per_article", 5)
    if current_calls >= max_calls:
        raise StateValidationError(f"Execution budget exceeded: max allowed calls per article is {max_calls}.")


def pre_tool_guardrail(tool_name: str, args: dict, current_calls: int = 0) -> None:
    """Execute all pre-tool guardrail checks."""
    check_tool_allowed(tool_name)
    check_call_budget(current_calls)

    url = args.get("url") or args.get("source_url") or args.get("profile_url")
    if url:
        validate_public_url(url)
