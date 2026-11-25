"""Part 03's config.py, moved into core/. Nothing changed: one Settings, read from .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "OnePercent Rates API"
    debug: bool = False
    rate_api_url: str = "https://openexchangerates.org"
    rate_api_key: str  # required — a missing key fails fast at startup


settings = Settings()
