from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Known default base URLs for popular LLM providers
PROVIDER_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "groq": "https://api.groq.com/openai/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "mistral": "https://api.mistral.ai/v1",
    "ollama": "http://localhost:11434/v1",
    "together": "https://api.together.xyz/v1",
    "togetherai": "https://api.together.xyz/v1",
    "perplexity": "https://api.perplexity.ai",
    "xai": "https://api.x.ai/v1",
    "grok": "https://api.x.ai/v1",
    "cohere": "https://api.cohere.ai/v1",
    "anthropic": "https://api.anthropic.com/v1",
}

# Known default models for popular LLM providers
PROVIDER_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "openrouter": "openai/gpt-4o-mini",
    "gemini": "gemini-3.6-flash",
    "google": "gemini-3.6-flash",
    "groq": "openai/gpt-oss-20b",
    "deepseek": "deepseek-chat",
    "mistral": "mistral-small-latest",
    "ollama": "llama3.2",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "togetherai": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "perplexity": "sonar",
    "xai": "grok-2-latest",
    "grok": "grok-2-latest",
    "cohere": "command-r",
    "anthropic": "claude-3-5-sonnet-20241022",
}


class Settings(BaseSettings):

    app_env: str = "development"

    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    search_provider: str = "tavily"
    tavily_api_key: str = ""

    database_url: str = "postgresql://postgres:postgres@localhost:5432/lead_intelligence"

    max_agent_iterations: int = 5
    max_llm_calls_per_article: int = 5
    request_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def resolve_provider_defaults(self) -> "Settings":
        provider_key = (self.llm_provider or "openai").lower().strip()

        # If base URL is not explicitly set, auto-resolve from provider
        if not self.llm_base_url:
            self.llm_base_url = PROVIDER_BASE_URLS.get(provider_key, "https://api.openai.com/v1")

        # If model is not explicitly set, auto-resolve default for provider
        if not self.llm_model:
            self.llm_model = PROVIDER_DEFAULT_MODELS.get(provider_key, "gpt-4o-mini")

        # Local Ollama typically requires no API key; supply a placeholder if blank
        if provider_key == "ollama" and not self.llm_api_key:
            self.llm_api_key = "ollama"

        return self


settings = Settings()