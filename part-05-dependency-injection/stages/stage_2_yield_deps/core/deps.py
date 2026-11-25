"""
The things a route can ASK for. FastAPI builds each one per request and hands it over.

A dependency is a question that must be answered before the route runs
("which page?", "which settings?", "who gets the live rates?").
Watch the terminal: every dependency prints when FastAPI calls it.
"""

from typing import Annotated

import httpx
from fastapi import Depends, Query

from ..services.rate_provider import RateProvider
from .config import Settings, get_settings

SettingsDep = Annotated[
    Settings, Depends(get_settings)
]  # name it once (the Part 03 Annotated trick)


# ── 1) a FUNCTION dependency ───────────────────────────────────────────
def pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    print("  pagination() called")
    return {"limit": limit, "offset": offset}


PageParams = Annotated[dict, Depends(pagination)]


# ── 2) a CLASS dependency: its __init__ params become ?min_rate=&max_rate= ──
class RateFilter:
    def __init__(self, min_rate: float = 0, max_rate: float | None = None):
        print("  RateFilter() built")
        self.min_rate = min_rate
        self.max_rate = max_rate


FilterDep = Annotated[RateFilter, Depends()]  # Depends() with no argument = "build this class"


# ── per REQUEST: a yield dependency opens the client, closes it after the response ──
async def get_http_client():
    async with httpx.AsyncClient(timeout=10) as client:  # ── setup
        print("  [http] client OPEN")
        try:
            yield client  # ── the route runs here
        finally:
            print("  [http] client CLOSED")  # ── teardown: after the response, even on error


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]


# ── 3) a dependency TREE: get_settings + get_http_client → get_rate_provider → route ──
def get_rate_provider(settings: SettingsDep, client: HttpClientDep) -> RateProvider:
    print("  get_rate_provider() called")
    return RateProvider(settings, client)


ProviderDep = Annotated[RateProvider, Depends(get_rate_provider)]
