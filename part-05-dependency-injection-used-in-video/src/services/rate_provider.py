"""
The live rate call from Part 03's /rates/live, moved out of the route into ONE place.

It's a service: no FastAPI imports. It takes the HTTP client and the settings as
plain parameters, so whoever calls it decides where those come from.
"""

import httpx

from ..core.config import Settings


class RateProviderError(Exception):
    """The provider is unreachable, rejected our key, or sent something unexpected."""


async def fetch_inr_rates(
    client: httpx.AsyncClient, settings: Settings
) -> dict[str, float]:
    """INR per 1 unit of every currency the provider knows, e.g. {"USD": 83.1, "EUR": 90.4}."""
    try:
        res = await client.get(
            f"{settings.rate_api_url}/api/latest.json",
            params={"app_id": settings.rate_api_key},
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise RateProviderError(
            f"rate provider unreachable ({exc.__class__.__name__})"
        ) from exc

    if res.status_code == 401:
        raise RateProviderError(
            "rate provider rejected RATE_API_KEY — put your real key in .env"
        )
    if res.status_code != 200:
        raise RateProviderError(f"rate provider answered {res.status_code}")

    per_usd = res.json().get("rates", {})  # the free plan's base is USD
    inr_per_usd = per_usd.get("INR")
    if not inr_per_usd:
        raise RateProviderError("rate provider sent no INR rate")
    return {
        code: round(inr_per_usd / value, 4) for code, value in per_usd.items() if value
    }


class RateProvider:
    """Knows HOW to get live rates. A route only asks for one (core/deps.py builds it)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient):
        self.settings = settings
        self.client = client  # handed in — the provider no longer opens its own

    async def inr_rates(self) -> dict[str, float]:
        return await fetch_inr_rates(self.client, self.settings)
