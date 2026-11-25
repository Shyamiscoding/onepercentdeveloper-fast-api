"""
STAGE 6 (notes A6) — background tasks: fire-and-forget AFTER the response.

Stage 5's folder, plus:
    routers/convert.py   POST /convert queues an audit log, then replies at once
    routers/rates.py     POST /rates/sync answers 202 Accepted; the live sync runs after
    routers/demo.py      demo — POST /demo/convert-slow: the same log done inline, the client waits

Try them in /docs and compare the response times; watch the terminal for the
📝 and 🔄 lines arriving after the response.

When NOT to use BackgroundTasks: work that must not be lost or takes minutes.
It runs in the SAME process after the response — if the server restarts, it's
gone. That kind of job belongs in a real queue (Celery, ARQ, a cloud queue).

This is the whole of Part 05. ../../src/ is this same app without the demo router.

Run:  uv run uvicorn stages.stage_6_background_tasks.main:app --reload     (needs .env — see stages/README.md)
"""

import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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
    title=f"{get_settings().app_name} — Stage 6 (background tasks)",
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
app.include_router(demo.router)
