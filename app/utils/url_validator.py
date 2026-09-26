import re
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import httpx
from pydantic import BaseModel, Field


class URLValidationResult(BaseModel):
    url: str
    normalized_url: Optional[str] = None
    platform: str = "other"  # "linkedin", "instagram", "facebook", "youtube", "other"
    is_valid_format: bool = False
    is_profile_type: bool = False
    is_reachable: bool = False
    verification_status: str = "UNVERIFIED"  # "VERIFIED", "UNVERIFIED", "INVALID", "BLOCKED_OR_UNVERIFIED", "IDENTITY_MISMATCH"
    confidence: float = 0.0
    rejection_reason: Optional[str] = None


# Tracking parameters to strip during normalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "igsh", "si", "ref", "s", "subId", "trackingId", "rcm", "fbclid",
    "gclid", "gclsrc", "_ga", "share_id", "originalSubdomain"
}

# Reserved Instagram system keywords (non-profile paths)
INSTAGRAM_SYSTEM_PATHS = {
    "explore", "reels", "reel", "p", "stories", "tv", "channel",
    "accounts", "account", "about", "legal", "directory", "developer",
    "press", "api", "shop", "direct", "create", "download", "privacy",
    "terms", "help", "graphql", "challenge"
}

# Reserved LinkedIn system path prefixes (non-personal profile paths)
LINKEDIN_NON_PERSONAL_PREFIXES = [
    "/company/", "/company-beta/", "/school/", "/showcase/",
    "/posts/", "/feed/", "/pulse/", "/activity/",
    "/sales/", "/jobs/", "/learning/", "/help/",
    "/legal/", "/safety/", "/about/", "/search/",
    "/pub/dir/", "/events/", "/groups/", "/checkout/", "/login/"
]

STOP_WORDS = {
    "the", "and", "co", "inc", "ltd", "pvt", "llp", "design", "studio",
    "interiors", "interior", "architects", "architecture", "associates",
    "official", "page", "profile", "com", "in"
}


def normalize_url(url: str) -> Optional[str]:
    """
    Normalizes a URL:
    - Converts scheme to https
    - Lowercases hostname
    - Strips tracking parameters
    - Normalizes regional LinkedIn subdomains if appropriate or preserves path
    - Removes trailing slash
    """
    if not url or not isinstance(url, str):
        return None

    cleaned_url = url.strip()
    if not cleaned_url:
        return None

    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = "https://" + cleaned_url

    try:
        parsed = urlparse(cleaned_url)
        scheme = "https"
        netloc = parsed.netloc.lower()

        # Strip default ports
        if netloc.endswith(":443"):
            netloc = netloc[:-4]
        elif netloc.endswith(":80"):
            netloc = netloc[:-3]

        # Clean query parameters
        qs = parse_qs(parsed.query, keep_blank_values=False)
        filtered_qs = {k: v for k, v in qs.items() if k.lower() not in TRACKING_PARAMS}
        new_query = urlencode(filtered_qs, doseq=True) if filtered_qs else ""

        # Normalize path
        path = parsed.path
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]

        normalized = urlunparse((scheme, netloc, path, parsed.params, new_query, ""))
        return normalized
    except Exception:
        return None


def extract_tokens(text: Optional[str]) -> set[str]:
    """Extract lowercase alphanumeric tokens from text, excluding common stop words."""
    if not text:
        return set()
    raw_tokens = set(re.findall(r"[a-zA-Z0-9]+", text.lower()))
    return {t for t in raw_tokens if t not in STOP_WORDS and len(t) > 1}


def _check_identity_match(
    handle: str,
    designer_name: Optional[str],
    studio_name: Optional[str],
    title: Optional[str] = None,
    snippet: Optional[str] = None
) -> Tuple[bool, float, Optional[str]]:
    """
    Checks whether a handle, title, or snippet reasonably matches the target designer or studio.
    """
    handle_lower = handle.lower().replace("_", "").replace("-", "").replace(".", "")
    target_tokens = extract_tokens(designer_name).union(extract_tokens(studio_name))

    if not target_tokens:
        # If no target name/studio is specified to match against, pass identity match with default confidence
        return True, 0.8, None

    # Check 1: Direct handle token or substring overlap
    handle_tokens = extract_tokens(handle)
    common_handle_tokens = handle_tokens.intersection(target_tokens)
    if common_handle_tokens:
        return True, 0.95, None

    # Check 2: Substring matching against concatenated designer or studio names
    clean_designer = re.sub(r"[^a-zA-Z0-9]", "", (designer_name or "").lower())
    clean_studio = re.sub(r"[^a-zA-Z0-9]", "", (studio_name or "").lower())

    if clean_designer and (clean_designer in handle_lower or handle_lower in clean_designer):
        return True, 0.95, None

    if clean_studio and (clean_studio in handle_lower or handle_lower in clean_studio):
        return True, 0.95, None

    # Check 3: Check title / snippet evidence if provided
    context_tokens = extract_tokens(title).union(extract_tokens(snippet))
    common_context_tokens = context_tokens.intersection(target_tokens)
    if len(common_context_tokens) >= 1:
        return True, 0.85, None

    # Check partial token match (at least 3 characters overlap)
    for target_tok in target_tokens:
        if len(target_tok) >= 3 and target_tok in handle_lower:
            return True, 0.80, None

    return False, 0.0, f"Social handle '{handle}' does not match target entity '{designer_name or studio_name}'"


def validate_social_url(
    url: Optional[str],
    designer_name: Optional[str] = None,
    studio_name: Optional[str] = None,
    title: Optional[str] = None,
    snippet: Optional[str] = None,
    check_live: bool = False,
    platform_target: str = "auto"
) -> URLValidationResult:
    """
    Validates a social media URL against platform, path type, reachability, and identity rules.
    """
    if not url:
        return URLValidationResult(
            url="",
            verification_status="INVALID",
            rejection_reason="URL is empty or missing"
        )

    norm_url = normalize_url(url)
    if not norm_url:
        return URLValidationResult(
            url=url,
            verification_status="INVALID",
            rejection_reason="Syntactically invalid URL"
        )

    parsed = urlparse(norm_url)
    netloc = parsed.netloc.lower()
    path = parsed.path

    # Platform identification
    platform = "other"
    if "linkedin.com" in netloc:
        platform = "linkedin"
    elif "instagram.com" in netloc:
        platform = "instagram"
    elif "facebook.com" in netloc:
        platform = "facebook"
    elif "youtube.com" in netloc:
        platform = "youtube"

    if platform_target != "auto" and platform != platform_target:
        return URLValidationResult(
            url=url,
            normalized_url=norm_url,
            platform=platform,
            is_valid_format=True,
            verification_status="INVALID",
            rejection_reason=f"URL is platform '{platform}', expected '{platform_target}'"
        )

    # Validate LinkedIn Personal Profile
    if platform == "linkedin":
        # Check if non-personal profile path
        for prefix in LINKEDIN_NON_PERSONAL_PREFIXES:
            if path.lower().startswith(prefix):
                return URLValidationResult(
                    url=url,
                    normalized_url=norm_url,
                    platform=platform,
                    is_valid_format=True,
                    is_profile_type=False,
                    verification_status="INVALID",
                    rejection_reason=f"LinkedIn URL path '{path}' is a non-personal profile page type ({prefix.strip('/')})"
                )

        match = re.match(r"^/in/([a-zA-Z0-9\-_%]+)", path, re.IGNORECASE)
        if not match:
            return URLValidationResult(
                url=url,
                normalized_url=norm_url,
                platform=platform,
                is_valid_format=True,
                is_profile_type=False,
                verification_status="INVALID",
                rejection_reason="LinkedIn URL path does not follow /in/<profile> format"
            )

        handle = match.group(1)
        # Identity match
        matched, confidence, reason = _check_identity_match(handle, designer_name, studio_name, title, snippet)
        if not matched:
            return URLValidationResult(
                url=url,
                normalized_url=norm_url,
                platform=platform,
                is_valid_format=True,
                is_profile_type=True,
                verification_status="IDENTITY_MISMATCH",
                confidence=confidence,
                rejection_reason=reason
            )

        # Reachability check if requested
        if check_live:
            reachable, status_code, live_reason = check_reachability(norm_url)
            if status_code in (999, 403, 429, 302):
                return URLValidationResult(
                    url=url,
                    normalized_url=norm_url,
                    platform=platform,
                    is_valid_format=True,
                    is_profile_type=True,
                    is_reachable=False,
                    verification_status="BLOCKED_OR_UNVERIFIED",
                    confidence=confidence * 0.7,
                    rejection_reason=live_reason
                )
            elif not reachable:
                return URLValidationResult(
                    url=url,
                    normalized_url=norm_url,
                    platform=platform,
                    is_valid_format=True,
                    is_profile_type=True,
                    is_reachable=False,
                    verification_status="INVALID" if status_code in (404, 410) else "UNVERIFIED",
                    confidence=0.0 if status_code in (404, 410) else confidence * 0.5,
                    rejection_reason=live_reason
                )

        return URLValidationResult(
            url=url,
            normalized_url=norm_url,
            platform=platform,
            is_valid_format=True,
            is_profile_type=True,
            is_reachable=True if check_live else False,
            verification_status="VERIFIED",
            confidence=confidence
        )

    # Validate Instagram Profile
    elif platform == "instagram":
        segments = [s for s in path.split("/") if s]
        if not segments:
            return URLValidationResult(
                url=url,
                normalized_url=norm_url,
                platform=platform,
                is_valid_format=True,
                is_profile_type=False,
                verification_status="INVALID",
                rejection_reason="Instagram URL missing username path segment"
            )

        handle = segments[0]
        if handle.lower() in INSTAGRAM_SYSTEM_PATHS:
            return URLValidationResult(
                url=url,
                normalized_url=norm_url,
                platform=platform,
                is_valid_format=True,
                is_profile_type=False,
                verification_status="INVALID",
                rejection_reason=f"Instagram URL handle '{handle}' is a reserved non-profile system path"
            )

        if not re.match(r"^[a-zA-Z0-9\._]{1,30}$", handle):
            return URLValidationResult(
                url=url,
                normalized_url=norm_url,
                platform=platform,
                is_valid_format=True,
                is_profile_type=False,
                verification_status="INVALID",
                rejection_reason=f"Instagram handle '{handle}' has invalid characters or length"
            )

        # Identity match
        matched, confidence, reason = _check_identity_match(handle, designer_name, studio_name, title, snippet)
        if not matched:
            return URLValidationResult(
                url=url,
                normalized_url=norm_url,
                platform=platform,
                is_valid_format=True,
                is_profile_type=True,
                verification_status="IDENTITY_MISMATCH",
                confidence=confidence,
                rejection_reason=reason
            )

        if check_live:
            reachable, status_code, live_reason = check_reachability(norm_url)
            if status_code in (999, 403, 429, 302):
                return URLValidationResult(
                    url=url,
                    normalized_url=norm_url,
                    platform=platform,
                    is_valid_format=True,
                    is_profile_type=True,
                    is_reachable=False,
                    verification_status="BLOCKED_OR_UNVERIFIED",
                    confidence=confidence * 0.7,
                    rejection_reason=live_reason
                )
            elif not reachable:
                return URLValidationResult(
                    url=url,
                    normalized_url=norm_url,
                    platform=platform,
                    is_valid_format=True,
                    is_profile_type=True,
                    is_reachable=False,
                    verification_status="INVALID" if status_code in (404, 410) else "UNVERIFIED",
                    confidence=0.0 if status_code in (404, 410) else confidence * 0.5,
                    rejection_reason=live_reason
                )

        return URLValidationResult(
            url=url,
            normalized_url=norm_url,
            platform=platform,
            is_valid_format=True,
            is_profile_type=True,
            is_reachable=True if check_live else False,
            verification_status="VERIFIED",
            confidence=confidence
        )

    # Generic or other platforms
    return URLValidationResult(
        url=url,
        normalized_url=norm_url,
        platform=platform,
        is_valid_format=True,
        is_profile_type=False,
        verification_status="UNVERIFIED",
        confidence=0.5
    )


def check_reachability(url: str, timeout: float = 5.0) -> Tuple[bool, int, str]:
    """
    Checks if a URL is reachable via HTTP request.
    Handles bot protection (999, 403, redirects to auth/login walls).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
            resp = client.head(url)
            if resp.status_code == 405:  # Method not allowed, try GET
                resp = client.get(url)

            status_code = resp.status_code
            final_url = str(resp.url)

            # Bot protection / auth wall detection
            if status_code in (999, 403, 429) or "authwall" in final_url or "/login" in final_url:
                return False, status_code, f"Platform bot protection / authwall triggered (HTTP {status_code})"

            if status_code in (404, 410):
                return False, status_code, f"Page not found (HTTP {status_code})"

            if 200 <= status_code < 400:
                return True, status_code, "Reachable"

            return False, status_code, f"HTTP status code {status_code}"

    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        return False, 0, f"Network connection error/timeout: {str(exc)}"
    except Exception as exc:
        return False, 0, f"Reachability check exception: {str(exc)}"
