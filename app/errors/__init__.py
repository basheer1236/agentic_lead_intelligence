"""
Error taxonomy for the Agentic AI Lead Intelligence system.
Categorizes exceptions into Retryable, Recoverable, and Fatal errors.
"""


class BasePipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


# ---------------------------------------------------------
# 1. RETRYABLE ERRORS
# Temporary failures suitable for automatic retry (timeouts, rate limits, 5xx)
# ---------------------------------------------------------

class RetryableError(BasePipelineError):
    """Base class for temporary, retryable errors."""
    pass


class HTTPTimeoutError(RetryableError):
    """Raised when an HTTP or API request times out."""
    pass


class RateLimitError(RetryableError):
    """Raised when an API rate limit (429) is encountered."""
    pass


class TemporaryServerError(RetryableError):
    """Raised when a temporary 5xx server error is returned by an API."""
    pass


# ---------------------------------------------------------
# 2. RECOVERABLE ERRORS
# Non-fatal failures where fallback, skipping, or partial completion is appropriate
# ---------------------------------------------------------

class RecoverableError(BasePipelineError):
    """Base class for non-fatal errors that can be handled gracefully."""
    pass


class ContentFetchError(RecoverableError):
    """Raised when article or web page content cannot be fetched."""
    pass


class SourceUnavailableError(RecoverableError):
    """Raised when an optional enrichment source is unreachable."""
    pass


class EnrichmentFailedError(RecoverableError):
    """Raised when designer enrichment fails for a specific source."""
    pass


# ---------------------------------------------------------
# 3. FATAL ERRORS
# Critical failures that unrecoverably halt pipeline execution
# ---------------------------------------------------------

class FatalError(BasePipelineError):
    """Base class for fatal, unrecoverable pipeline errors."""
    pass


class InvalidConfigurationError(FatalError):
    """Raised when required settings or API keys are missing or invalid."""
    pass


class StateValidationError(FatalError):
    """Raised when graph state or input validation fails unrecoverably."""
    pass
