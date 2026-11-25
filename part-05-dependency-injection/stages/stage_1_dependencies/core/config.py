"""Part 03's Settings, now handed out by a function instead of a global."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "OnePercent Rates API"
    debug: bool = False
    rate_api_url: str = "https://openexchangerates.org"
    rate_api_key: str  # required — a missing key fails fast at startup


@lru_cache
def get_settings() -> Settings:
    return Settings()  # .env is read ONCE per process, then reused
