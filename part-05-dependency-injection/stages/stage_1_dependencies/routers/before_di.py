"""
Stage 1 demo only — the PROBLEM, so /docs can compare it with routers/rates.py.

ONE endpoint, grown step by step — and ALWAYS the live list (~170 currencies). The data
source never changes under the student mid-lesson: it's the same live list all the way down.
    /before/rates/live-full   the WHOLE live list (~170) — why we page at all
    /before/rates             paging by hand: take limit & offset, slice THAT live list
    /before/rates/search      the SAME live list, filtered — limit & offset copy-pasted
    /before/rates/plain       first instinct: one reusable slicing function (params STILL repeated)
    /before/rates/live        settings + an HTTP client built inside the route

Every route fetches the live list itself and does everything itself. Not carried into
stage 2 — dependency injection (routers/rates.py + core/deps.py) is the fix.
"""

from typing import Annotated

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from ..core.config import Settings
from ..services.rate_provider import RateProviderError, fetch_inr_rates

router = APIRouter(prefix="/before", tags=["0 · before DI"])


async def live_rates() -> dict[str, float]:
    """The live list — a fresh Settings + client, fetched by hand on every call."""
    settings = Settings()  # ← same hidden setup, repeated on every call
    async with httpx.AsyncClient() as client:
        try:
            return await fetch_inr_rates(client, settings)
        except RateProviderError as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc


@router.get("/rates/live-full")
async def live_full():
    """The WHOLE live list — ~170 currencies, nothing left out. THIS is what real data looks like."""
    rates = await live_rates()
    return {"count": len(rates), "items": rates}  # no paging: the entire list in one response


@router.get("/rates")
async def before_list(
    limit: Annotated[int, Query(ge=1, le=100)] = 10, offset: Annotated[int, Query(ge=0)] = 0
):
    rates = await live_rates()  # the SAME ~170-row live list as above
    items = list(rates.items())[offset : offset + limit]  # take limit & offset, then slice
    return {"items": dict(items), "limit": limit, "offset": offset}


@router.get("/rates/search")
async def before_search(
    min_rate: float = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,  # ← copy-pasted
    offset: Annotated[int, Query(ge=0)] = 0,
):  # ← copy-pasted
    rates = await live_rates()  # the SAME live list again
    hits = [(c, r) for c, r in rates.items() if r >= min_rate]
    return {"items": dict(hits[offset : offset + limit]), "total": len(hits)}


def paginate(items: list, limit: int, offset: int) -> dict:
    """First instinct: pull the repeated SLICING into one plain function."""
    return {"items": dict(items[offset : offset + limit]), "limit": limit, "offset": offset}


@router.get("/rates/plain")
async def before_plain(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,  # ← STILL declared here…
    offset: Annotated[int, Query(ge=0)] = 0,
):  # ← …and in every other list route
    # the slicing is written once now, but a plain function can't read the query string,
    # so each route STILL declares limit & offset and STILL calls paginate() itself.
    rates = await live_rates()
    return paginate(list(rates.items()), limit, offset)


@router.get("/rates/live")
async def before_live(to: str = "USD"):
    settings = Settings()  # ← reads .env on EVERY request
    async with httpx.AsyncClient() as client:  # ← builds its own client
        try:
            rates = await fetch_inr_rates(client, settings)
        except RateProviderError as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"to": to.upper(), "inr_per_unit": round(rates[to.upper()], 2)}
    # and a test can't swap any of this for a fake — it's all hidden inside the route
