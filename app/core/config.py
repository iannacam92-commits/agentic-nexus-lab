"""Nexus AI Lab — application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    xai_api_key: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./nexus_lab.db"

    # Redis (for job queue)
    redis_url: str = "redis://localhost:6379/0"

    # App
    log_level: str = "INFO"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["*"]

    # Study defaults
    default_temperature: float = 0.7
    default_seed: int = 42
    default_max_tokens: int = 1024
    run_timeout_seconds: int = 60

    # Studies path
    studies_dir: str = "studies"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
