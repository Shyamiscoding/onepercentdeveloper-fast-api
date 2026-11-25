"""
STAGE 4 (notes A4) — lifespan: run code ONCE at startup and shutdown.

Stage 3's folder, plus:
    main.py              + lifespan: opens ONE http client, loads the live rates once
    core/deps.py         get_http_client now hands out that shared client (no yield, no setup)
    routers/health.py    NEW — GET /uptime
    routers/demo.py      demo — GET /demo/client-id

The question of this whole part: WHERE should a thing live?
    per CALL      stage 1   RateProvider opened a new client inside every call
    per REQUEST   stage 2   a yield dependency opened one, closed it after the response
    per PROCESS   HERE      lifespan opens ONE at startup, every request shares it,
                            shutdown closes it  ← right for clients, pools, ML models
    FOREVER       Part 06   the database
Only core/deps.py changed between those three. The routes never noticed.

If the provider is down or the key is wrong, startup keeps the built-in rates
and says so — a broken provider must not stop the app from starting.

    GET /uptime          when startup ran, and "rates_source": "live" or "fallback"
    GET /demo/client-id  twice → the same id = one shared client
Stop the server with Ctrl+C and watch SHUTDOWN print.

Run:  uv run uvicorn stages.stage_4_lifespan.main:app --reload     (needs .env — see stages/README.md)
"""

from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
from fastapi import Depends, FastAPI

from .core.config import get_settings
from .core.deps import log_request
from .routers import admin, convert, demo, health, rates
from .services import rates as rate_service
from .services.rate_provider import RateProvider, RateProviderError


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP: opening ONE http client for the whole app…")
    app.state.http = httpx.AsyncClient(timeout=10)
    try:
        # WE call these here, so they get plain arguments — no Depends at startup
        await rate_service.sync_from_provider(RateProvider(get_settings(), app.state.http))
        app.state.rates_source = "live"
    except RateProviderError as exc:
        print(f"STARTUP: provider failed ({exc}) — keeping the built-in rates")
        app.state.rates_source = "fallback"
    app.state.started_at = datetime.now(UTC)
    print(f"STARTUP: done ({app.state.rates_source} rates) — now serving requests")
    yield  # ── the app runs here
    print("SHUTDOWN: closing the http client")
    await app.state.http.aclose()


app = FastAPI(
    title=f"{get_settings().app_name} — Stage 4 (lifespan)",
    dependencies=[Depends(log_request)],
    lifespan=lifespan,
)

app.include_router(rates.router)
app.include_router(admin.router)
app.include_router(convert.router)
app.include_router(health.router)
app.include_router(demo.router)
