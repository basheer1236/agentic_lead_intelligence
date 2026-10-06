"""
Interactive Environment Initialization Script for Agentic Lead Intelligence.
Checks for .env file and interactively guides new users through setting up required API keys.
"""

import os
from pathlib import Path

ENV_PATH = Path(".env")
EXAMPLE_PATH = Path(".env.example")


def init_environment():
    print("=" * 60)
    print("AGENTIC LEAD INTELLIGENCE - ENVIRONMENT SETUP WIZARD")
    print("=" * 60)

    existing_config = {}

    if ENV_PATH.exists():
        print("[+] Existing .env file found. Checking configuration...\n")
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    existing_config[key.strip()] = val.strip()

    # Prompt for missing or default parameters
    def get_setting(key, description, default_val):
        curr = existing_config.get(key, "")
        if curr and curr != f"your_{key.lower()}_here":
            print(f"  ✓ {key} is configured.")
            return curr

        print(f"\n[?] Configuration needed: {key}")
        print(f"    Description: {description}")

        user_val = input(f"    Enter value [{default_val}]: ").strip()
        if not user_val:
            user_val = default_val

        return user_val

    app_env = get_setting("APP_ENV", "Environment mode (production/development)", "production")
    db_url = get_setting(
        "DATABASE_URL",
        "PostgreSQL / Neon connection string",
        "postgresql://neondb_owner:npg_eQtZ6B7FmknT@ep-lucky-sound-b4drbw0w-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )
    llm_provider = get_setting("LLM_PROVIDER", "LLM Provider (gemini/openrouter/groq/openai)", "gemini")
    llm_api_key = get_setting("LLM_API_KEY", "LLM API Key", "")
    llm_model = get_setting("LLM_MODEL", "LLM Model Name", "gemini-flash-latest")
    tavily_key = get_setting("TAVILY_API_KEY", "Tavily Search API Key (optional)", "")

    # Save to .env
    env_content = f"""# Auto-generated .env configuration
APP_ENV={app_env}

DATABASE_URL={db_url}

LLM_PROVIDER={llm_provider}
LLM_API_KEY={llm_api_key}
LLM_BASE_URL=
LLM_MODEL={llm_model}

SEARCH_PROVIDER=tavily
TAVILY_API_KEY={tavily_key}

MAX_AGENT_ITERATIONS=5
MAX_LLM_CALLS_PER_ARTICLE=5
REQUEST_TIMEOUT_SECONDS=20
"""

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(env_content)

    print("\n" + "=" * 60)
    print("SUCCESS: Environment file '.env' configured successfully!")
    print("=" * 60)


if __name__ == "__main__":
    init_environment()
