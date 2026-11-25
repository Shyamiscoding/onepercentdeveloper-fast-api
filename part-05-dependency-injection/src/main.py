"""
OnePercent FastAPI course — Part 05, the FINISHED app: Part 04's layout, wired with dependencies.

This is stage 6 without its demo router. Same endpoints as Part 03, now:
    split by job             routers (thin) → services (fat) → schemas    (Part 04)
    wired with Depends       settings, the rate provider, paging, filters       (A1)
    cleaned up per request   yield dependencies                                 (A2)
    guarded                  /admin/rates and POST /rates/sync need x-api-key   (A3)
    set up once              ONE HTTP client for the whole process              (A4)
    middleware + CORS        timing header, a browser frontend can call us      (A5)
    background work          the audit log and the live sync run after the reply (A6)

Where each thing lives — the mental model of this part:
    per CALL      the amount being converted          (plain arguments)
    per REQUEST   whatever a yield dependency opens   (yield dependency)
    per PROCESS   settings, the HTTP client           (lifespan / lru_cache)
    FOREVER       nothing yet! Restart the server: every rate you changed is gone.
                  That's Part 06 — a real database.

Run (from part-05-dependency-injection/):
    cp ../part-04-structure-and-di/.env .env  # once — it has your RATE_API_KEY
    uv run uvicorn src.main:app --reload      # → http://127.0.0.1:8000/docs
"""

import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.deps import log_request
from .routers import admin, convert, health, rates
from .services import rates as rate_service
from .services.rate_provider import RateProvider, RateProviderError


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP: opening ONE http client for the whole app…")
    app.state.http = httpx.AsyncClient(timeout=10)
    try:
        await rate_service.sync_from_provider(RateProvider(get_settings(), app.state.http))
        app.state.rates_source = "live"
    except RateProviderError as exc:
        print(f"STARTUP: provider failed ({exc}) — keeping the built-in rates")
        app.state.rates_source = "fallback"
    app.state.started_at = datetime.now(UTC)
    print(f"STARTUP: done ({app.state.rates_source} rates) — now serving requests")
    yield
    print("SHUTDOWN: closing the http client")
    await app.state.http.aclose()


app = FastAPI(
    title=get_settings().app_name,
    version="4.0.0",
    dependencies=[Depends(log_request)],
    lifespan=lifespan,
)


@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)  # ── the route runs here
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response


# added LAST → outermost: it answers the browser's preflight before anything else
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # exact origin: scheme + host + port
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,  # so never allow_origins=["*"] with this
    expose_headers=["X-Process-Time-ms"],  # custom headers are hidden from JS unless exposed
)

app.include_router(rates.router)
app.include_router(admin.router)
app.include_router(convert.router)
app.include_router(health.router)
