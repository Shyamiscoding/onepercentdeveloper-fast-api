"""/rates — Part 03's CRUD and live rate, now THIN: read the request, call a service, return."""

from typing import Annotated

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ..core.config import settings
from ..schemas.rates import Currency, RateIn
from ..services import rates as rate_service
from ..services.rate_provider import RateProviderError, fetch_inr_rates

# prefix + tags apply to EVERY route below — no more repeating "/rates"
router = APIRouter(prefix="/rates", tags=["rates app"])


@router.get("")  # GET /rates — was @app.get("/rates")
def list_rates(limit: Annotated[int, Query(ge=1, le=100)] = 10):
    return rate_service.all_rates(limit)


@router.get("/live")  # before /{code}, or "live" would match {code}
async def live_rate(to: Currency = Currency.usd):
    # still exactly like Part 03: a NEW client for every call. Stages 2, 3 and 5 fix that.
    async with httpx.AsyncClient() as client:
        try:
            rates = await fetch_inr_rates(client, settings)
        except RateProviderError as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"to": to.value, "inr_per_unit": round(rates[to.value], 2), "source": "live"}


@router.get("/{code}")
def get_rate(code: str):
    rate = rate_service.get_rate(code)
    if rate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
    return {"code": code.upper(), "inr_per_unit": rate}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_rate(rate: RateIn):
    rate_service.set_rate(rate.code, rate.inr_per_unit)
    return rate


@router.put("/{code}")
def update_rate(code: str, rate: RateIn):
    if rate_service.get_rate(code) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
    rate_service.set_rate(code, rate.inr_per_unit)
    return rate


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rate(code: str):
    if not rate_service.delete_rate(code):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
