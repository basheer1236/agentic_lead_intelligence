import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.config.settings import Settings, PROVIDER_BASE_URLS
from app.llm.client import LLMClient
from unittest.mock import patch


def test_universal_provider_defaults():
    # OpenRouter
    s = Settings(llm_provider="openrouter", llm_api_key="key", llm_base_url="", llm_model="")
    assert s.llm_base_url == "https://openrouter.ai/api/v1"
    assert s.llm_model == "openai/gpt-4o-mini"

    # Gemini
    s = Settings(llm_provider="gemini", llm_api_key="key", llm_base_url="", llm_model="")
    assert s.llm_base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert s.llm_model == "gemini-flash-latest"

    # Groq
    s = Settings(llm_provider="groq", llm_api_key="key", llm_base_url="", llm_model="")
    assert s.llm_base_url == "https://api.groq.com/openai/v1"
    assert s.llm_model == "llama-3.3-70b-versatile"

    # DeepSeek
    s = Settings(llm_provider="deepseek", llm_api_key="key", llm_base_url="", llm_model="")
    assert s.llm_base_url == "https://api.deepseek.com/v1"
    assert s.llm_model == "deepseek-chat"

    # Ollama
    s = Settings(llm_provider="ollama", llm_api_key="", llm_base_url="", llm_model="")
    assert s.llm_base_url == "http://localhost:11434/v1"
    assert s.llm_api_key == "ollama"

    # Custom model and endpoint override
    s = Settings(
        llm_provider="custom-ai",
        llm_api_key="custom-key",
        llm_base_url="https://ai.custom.corp/v1",
        llm_model="custom-expert-v1",
    )
    assert s.llm_base_url == "https://ai.custom.corp/v1"
    assert s.llm_model == "custom-expert-v1"


def test_client_initialization_openrouter():
    from app.config.settings import settings
    with patch.object(settings, "llm_provider", "openrouter"), \
         patch.object(settings, "llm_api_key", "sk-or-v1-mock"), \
         patch.object(settings, "llm_base_url", "https://openrouter.ai/api/v1"), \
         patch.object(settings, "llm_model", "anthropic/claude-3.5-sonnet"):
        client = LLMClient()
        assert client.provider == "openrouter"
        assert client.model == "anthropic/claude-3.5-sonnet"
        assert not client.is_native_anthropic


def test_client_initialization_anthropic():
    from app.config.settings import settings
    with patch.object(settings, "llm_provider", "anthropic"), \
         patch.object(settings, "llm_api_key", "sk-ant-mock"), \
         patch.object(settings, "llm_base_url", "https://api.anthropic.com/v1"), \
         patch.object(settings, "llm_model", "claude-3-5-sonnet-20241022"):
        client = LLMClient()
        assert client.provider == "anthropic"
        assert client.is_native_anthropic


if __name__ == "__main__":
    test_universal_provider_defaults()
    test_client_initialization_openrouter()
    test_client_initialization_anthropic()
    print("All universal LLM tests passed successfully!")
