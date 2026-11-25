"""Part 03's config.py, moved into core/. Nothing changed: one Settings, read from .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "OnePercent Rates API"
    debug: bool = False
    rate_api_url: str = "https://openexchangerates.org"
    rate_api_key: str  # required — a missing key fails fast at startup
    admin_api_key: str = "secret"  # from .env; the real login arrives in Part 07


@lru_cache
def get_settings() -> Settings:
    return Settings()  # .env is read ONCE per process, then reused


# module-level instance so `from .core.config import settings` works (used by main.py)
settings = get_settings()
