from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_env: str = "development"

    llm_provider: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str

    search_provider: str = "tavily"
    tavily_api_key: str = ""

    database_url: str

    max_agent_iterations: int = 5
    max_llm_calls_per_article: int = 5
    request_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()