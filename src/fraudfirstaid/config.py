"""All settings come from environment variables (or a local .env file)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "fraudfirstaid"
    app_env: Literal["local", "ci", "production"]
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    data_file: Path = Path("data/sample_records.json")
    database_url: str | None = None
    git_sha: str = "dev"

    # LLM gateway (Day 8). Keys default to empty so tests and CI never need them.
    gemini_api_key: str = ""
    groq_api_key: str = ""
    llm_primary_model: str = "gemini-3.8-flash"
    llm_fallback_model: str = "openai/gpt-oss-20b"

    # Both providers speak the OpenAI API.
    llm_primary_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    llm_fallback_base_url: str = "https://api.groq.com/openai/v1"

    llm_timeout_seconds: float = 30.0
    usd_inr: float = 95.0
    prompts_dir: Path = Path("prompts")


@lru_cache
def get_settings() -> Settings:
    """Build the settings once and reuse them."""
    return Settings()
