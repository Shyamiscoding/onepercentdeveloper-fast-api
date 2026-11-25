"""
STAGE 1 (notes A1) — Dependency Injection: declare what you need, FastAPI builds it.

Part 04's stage_1_layout folder, plus:
    core/config.py             get_settings() with lru_cache, instead of a global
    core/deps.py               NEW — everything a route can ask for:
                                 PageParams   a function dependency (pagination)
                                 FilterDep    a class dependency (min/max rate)
                                 ProviderDep  a tree: get_settings → get_rate_provider
    services/rate_provider.py  + RateProvider, the thing routes ask for
    routers/rates.py           routes ask instead of build; + GET /rates/search
    routers/before_di.py       demo — the same routes WITHOUT DI, to compare
    routers/demo.py            demo — per-request caching and THE RULE

/docs groups:
    "0 · before DI"   /before/rates/live-full, /before/rates, /before/rates/search,
                      /before/rates/plain, /before/rates/live
    "rates"           the real routes, now with Depends
    "with DI"         /demo/cache — asked for twice, runs ONCE per request
    "the rule"        /demo/wrong-call, /demo/right-call-1, /demo/right-call-2

Watch the terminal: every dependency prints when FastAPI calls it.

Run:  uv run uvicorn stages.stage_1_dependencies.main:app --reload     (needs .env — see stages/README.md)
"""

from fastapi import FastAPI

from .core.config import get_settings
from .routers import before_di, convert, demo, rates

# at import time WE call get_settings(), so it's a plain call — no Depends here
app = FastAPI(title=f"{get_settings().app_name} — Stage 1 (dependencies)")

app.include_router(rates.router)
app.include_router(convert.router)
app.include_router(before_di.router)
app.include_router(demo.router)
