"""
STAGE 6 (notes B4) — settings from .env, used for real.

pydantic-settings reads env vars / .env with the SAME validation you know. The
app title comes from settings, and GET /rates/live uses settings.rate_api_url +
settings.rate_api_key to call a real 3rd-party exchange-rate API. (That network
wait is exactly why the handler is `async` — see Stage 8.)

Setup:  cp .env.example .env    (then put a real RATE_API_KEY in it)
Run:    uv run uvicorn stages.stage_6_settings:app --reload
"""

from enum import StrEnum

import httpx
from config import settings
from fastapi import FastAPI, HTTPException

app = FastAPI(title=settings.app_name)  # NEW: title from validated settings


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


@app.get("/settings")  # peek at the non-secret config
def show_settings():
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "rate_api_url": settings.rate_api_url,
    }


@app.get("/rates/live")  # uses settings to call the 3rd-party API
async def live_rate(to: Currency = Currency.usd):

    params = {"app_id": settings.rate_api_key}

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{settings.rate_api_url}/api/latest.json", params=params)

    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="rate provider unavailable")

    print(res.json())
    rates = res.json().get("rates", {})
    inr_per_usd = rates.get("INR")
    to_per_usd = rates.get(to.value)  # units of `to` per 1 USD

    if inr_per_usd is None or not to_per_usd:
        raise HTTPException(status_code=502, detail="rate unavailable for this currency")
    return {
        "to": to.value,
        "inr_per_unit": round(inr_per_usd / to_per_usd, 2),  # INR per 1 unit of `to`
        "source": "live",
    }
