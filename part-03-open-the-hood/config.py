"""
OnePercent FastAPI course — Part 03 (B4): configuration the right way.

`BaseSettings` reads values from environment variables and a .env file, with the
SAME Pydantic validation you already know. Secrets never live in code or git.

These are exactly the values Part 03 uses — nothing speculative. `main.py` reads
`rate_api_url` + `rate_api_key` in the GET /rates/live endpoint to call a real
3rd-party exchange-rate API (that's Section C's async example).

pydantic-settings is installed by the root `uv sync`.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "OnePercent Rates API"  # used as the FastAPI title
    debug: bool = False  # "1"/"true"/"yes" -> True (bool coercion)

    # external exchange-rate API, used by GET /rates/live.
    # grab a free key (App ID): https://openexchangerates.org
    rate_api_url: str = "https://openexchangerates.org"
    rate_api_key: str  # required — no default, so a missing key fails fast at startup


# built ONCE, validated at import time. Field names map to UPPER_CASE env vars.
settings = Settings()
