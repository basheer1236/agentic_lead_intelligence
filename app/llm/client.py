import logging
from openai import OpenAI, APIError, APITimeoutError, RateLimitError as OpenAIRateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.settings import settings
from app.errors import (
    InvalidConfigurationError,
    HTTPTimeoutError,
    RateLimitError,
    TemporaryServerError,
)

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False


class LLMClient:
    """
    Universal LLM Client supporting any provider, API key, and model.
    Seamlessly routes between OpenAI-compatible endpoints (OpenAI, OpenRouter,
    Gemini, Groq, DeepSeek, Mistral, Ollama, Together, Perplexity, custom endpoints)
    and native providers (Anthropic).
    """

    def __init__(self):
        from app.config.settings import PROVIDER_BASE_URLS
        self.provider = (settings.llm_provider or "openai").lower().strip()
        self.api_key = settings.llm_api_key.strip() if settings.llm_api_key else ""
        raw_base_url = settings.llm_base_url.strip() if settings.llm_base_url else ""
        self.base_url = raw_base_url or PROVIDER_BASE_URLS.get(self.provider, "https://api.openai.com/v1")
        self.model = settings.llm_model.strip() if settings.llm_model else ""

        if not self.api_key:
            raise InvalidConfigurationError(
                "Missing required LLM API key. Please specify LLM_API_KEY in your .env file."
            )

        if not self.model:
            raise InvalidConfigurationError(
                f"Missing LLM model name for provider '{self.provider}'. Please specify LLM_MODEL in .env."
            )

        # Determine client engine: Native Anthropic vs OpenAI-compatible
        self.is_native_anthropic = False
        if self.provider == "anthropic" and "anthropic.com" in self.base_url:
            if not ANTHROPIC_AVAILABLE:
                raise InvalidConfigurationError(
                    "The 'anthropic' package is required for native Anthropic provider. "
                    "Run 'pip install anthropic' or use OpenRouter instead."
                )
            self.anthropic_client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=settings.request_timeout_seconds,
            )
            self.is_native_anthropic = True
            logger.info("LLMClient initialized using native Anthropic client for model: %s", self.model)
        else:
            # Universal OpenAI-compatible client
            default_headers = {}
            if self.provider == "openrouter":
                default_headers = {
                    "HTTP-Referer": "https://github.com/basheer7526/agentic-lead-intelligence",
                    "X-Title": "Agentic Lead Intelligence",
                }

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or None,
                default_headers=default_headers if default_headers else None,
                timeout=max(settings.request_timeout_seconds, 60),
            )
            logger.info(
                "LLMClient initialized for provider '%s' (base_url: %s, model: %s)",
                self.provider,
                self.base_url,
                self.model,
            )

    @retry(
        stop=stop_after_attempt(8),
        wait=wait_exponential(multiplier=2, min=5, max=60),
        retry=retry_if_exception_type((HTTPTimeoutError, RateLimitError, TemporaryServerError)),
        reraise=True,
    )
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate completions across any provider and model.
        """
        if self.is_native_anthropic:
            return self._generate_anthropic(system_prompt, user_prompt)
        if self.provider in ("gemini", "google"):
            return self._generate_gemini_native(system_prompt, user_prompt)
        return self._generate_openai_compatible(system_prompt, user_prompt)

    def _generate_gemini_native(self, system_prompt: str, user_prompt: str) -> str:
        import json
        import urllib.request
        import urllib.error

        models_to_try = [
            self.model,
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-flash-latest",
        ]
        seen = set()
        ordered_models = []
        for m in models_to_try:
            clean_m = (m or "").replace("models/", "").strip()
            if clean_m and clean_m not in seen:
                seen.add(clean_m)
                ordered_models.append(clean_m)

        last_err = None
        for m in ordered_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            payload_dict = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "generationConfig": {"temperature": 0.0},
            }
            if system_prompt and system_prompt.strip():
                payload_dict["system_instruction"] = {
                    "parts": [{"text": system_prompt.strip()}]
                }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload_dict).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=max(settings.request_timeout_seconds, 30)) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "")
                            if text:
                                self.model = m
                                return text
            except urllib.error.HTTPError as exc:
                err_body = ""
                try:
                    err_body = exc.read().decode("utf-8")
                except Exception:
                    pass
                err_msg = f"HTTP {exc.code} {exc.reason}: {err_body}".lower()
                last_err = exc
                if exc.code == 429 or "rate limit" in err_msg:
                    raise RateLimitError(f"Gemini API rate limit exceeded: {err_body}") from exc
                if exc.code == 400 and ("api_key_invalid" in err_msg or "invalid api key" in err_msg):
                    raise InvalidConfigurationError(f"Invalid Gemini API Key: {err_body}") from exc
                if exc.code in (404, 503):
                    continue
                raise TemporaryServerError(f"Gemini API error: {err_body}") from exc
            except Exception as exc:
                last_err = exc
                continue

        if last_err:
            raise TemporaryServerError(f"Gemini API error: {last_err}") from last_err
        raise TemporaryServerError("Gemini API returned an empty response.")

    def _generate_openai_compatible(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            msg = response.choices[0].message
            content = getattr(msg, "content", None) or ""
            if not content.strip() and hasattr(msg, "reasoning") and getattr(msg, "reasoning", None):
                content = getattr(msg, "reasoning")
            return content

        except APITimeoutError as exc:
            raise HTTPTimeoutError(f"LLM API request timed out for provider '{self.provider}'.") from exc

        except OpenAIRateLimitError as exc:
            raise RateLimitError(f"LLM API rate limit exceeded for provider '{self.provider}'.") from exc

        except APIError as exc:
            err_msg = str(exc).lower()
            if "rate limit" in err_msg or "429" in err_msg:
                raise RateLimitError(f"LLM API rate limit exceeded: {exc}") from exc
            if "401" in err_msg or "unauthorized" in err_msg or "invalid api key" in err_msg:
                raise InvalidConfigurationError(f"Invalid LLM API Key: {exc}") from exc
            if "404" in err_msg or "not found" in err_msg or "no longer available" in err_msg:
                raise InvalidConfigurationError(f"LLM model not found or unavailable: {exc}") from exc
            raise TemporaryServerError(f"LLM API server error: {exc}") from exc

        except Exception as exc:
            err_msg = str(exc).lower()
            if "rate limit" in err_msg or "429" in err_msg:
                raise RateLimitError(f"LLM API rate limit exceeded: {exc}") from exc
            if "404" in err_msg or "not found" in err_msg or "no longer available" in err_msg:
                raise InvalidConfigurationError(f"LLM model unavailable: {exc}") from exc
            if "401" in err_msg or "unauthorized" in err_msg:
                raise InvalidConfigurationError(f"Invalid LLM API Key: {exc}") from exc
            raise

    def _generate_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            parts = []
            for block in response.content:
                if hasattr(block, "text"):
                    parts.append(block.text)
            return "".join(parts)

        except Exception as exc:
            if ANTHROPIC_AVAILABLE:
                if isinstance(exc, anthropic.RateLimitError):
                    raise RateLimitError("Anthropic API rate limit exceeded.") from exc
                if isinstance(exc, anthropic.APITimeoutError):
                    raise HTTPTimeoutError("Anthropic API request timed out.") from exc
                if isinstance(exc, anthropic.APIError):
                    raise TemporaryServerError(f"Anthropic API server error: {exc}") from exc
            raise