"""/rates — Part 03's CRUD and live rate, now THIN: read the request, call a service, return."""

import httpx
from fastapi import APIRouter, HTTPException, status

from ..core.config import Settings
from ..core.deps import PageParams
from ..schemas.rates import Currency, RateIn
from ..services import rates as rate_service
from ..services.rate_provider import RateProviderError, fetch_inr_rates

# prefix + tags apply to EVERY route below — no more repeating "/rates"
router = APIRouter(prefix="/rates", tags=["rates app"])


async def live_rates() -> dict[str, float]:
    """The live list — a fresh Settings + client, fetched by hand on every call."""
    settings = Settings()  # ← same hidden setup, repeated on every call
    async with httpx.AsyncClient() as client:
        try:
            return await fetch_inr_rates(client, settings)
        except RateProviderError as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc


import asyncio

from fastapi import BackgroundTasks, Depends

from ..core.config import get_settings
from ..core.deps import HttpClientDep, ProviderDep, require_api_key
from ..schemas.rates import RatePage, RatePublic


async def log_hit(count: int):
    await asyncio.sleep(2)  # stand-in for a slow logging service
    print(f"  📝 served {count} rates — logged AFTER the reply")


@router.get(
    "/live-full", response_model=RatePage, dependencies=[Depends(require_api_key)]
)
async def live_full(page: PageParams, provider: ProviderDep, bg: BackgroundTasks):
    try:
        rates = await provider.inr_rates()
    except RateProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    window = list(rates.items())[page["offset"] : page["offset"] + page["limit"]]
    rows = [RatePublic(code=c, inr_per_unit=r) for c, r in window]
    bg.add_task(log_hit, len(rates))
    return RatePage(items=rows, total=len(rates), **page)


def paginate(items: list, limit: int, offset: int) -> dict:
    """First instinct: pull the repeated SLICING into one plain function."""
    return {
        "items": dict(items[offset : offset + limit]),
        "limit": limit,
        "offset": offset,
        "total": len(items),
    }


@router.get("/search")
async def search(
    page: PageParams,
    client: HttpClientDep,
    min_rate: float = 0,
):
    try:
        rates = await fetch_inr_rates(client, get_settings())
    except RateProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    hits = [(c, r) for c, r in rates.items() if r >= min_rate]
    return paginate(hits, page["limit"], page["offset"])


@router.get("")  # GET /rates — was @app.get("/rates")
def list_rates(bg: BackgroundTasks):
    bg.add_task(log_hit, len(rate_service.all_rates()))
    return rate_service.all_rates()


@router.get("/live")  # before /{code}, or "live" would match {code}
async def live_rate(to: Currency = Currency.usd):
    settings = Settings()  # ← same hidden setup as every route below
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
