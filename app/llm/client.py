from openai import OpenAI, APIError, APITimeoutError, RateLimitError as OpenAIRateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.settings import settings
from app.errors import (
    InvalidConfigurationError,
    HTTPTimeoutError,
    RateLimitError,
    TemporaryServerError,
)


class LLMClient:

    def __init__(self):
        if not settings.llm_api_key or not settings.llm_base_url or not settings.llm_model:
            raise InvalidConfigurationError(
                "Missing required LLM configuration (llm_api_key, llm_base_url, llm_model)."
            )

        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=3, max=30),
        retry=retry_if_exception_type((HTTPTimeoutError, RateLimitError, TemporaryServerError)),
        reraise=True,
    )
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""

        except APITimeoutError as exc:
            raise HTTPTimeoutError("LLM API request timed out.") from exc

        except OpenAIRateLimitError as exc:
            raise RateLimitError("LLM API rate limit exceeded.") from exc

        except APIError as exc:
            if "rate limit" in str(exc).lower() or "429" in str(exc):
                raise RateLimitError("LLM API rate limit exceeded.") from exc
            raise TemporaryServerError(f"LLM API server error: {exc}") from exc

        except Exception as exc:
            if "rate limit" in str(exc).lower() or "429" in str(exc):
                raise RateLimitError("LLM API rate limit exceeded.") from exc
            raise