"""
STAGE 5 (notes A5) — middleware & CORS.

Stage 4's folder, plus two middlewares in main.py (stage 4's demo is gone):
    a custom timing middleware  -> adds an X-Process-Time-ms header to every response
    CORSMiddleware              -> lets a browser page on http://localhost:3000 call us

SEE CORS for real (two terminals, from the part-04 folder):
    1) uv run uvicorn stages.stage_5_cors_middleware.main:app --reload
    2) cd stages && python -m http.server 3000
Open http://localhost:3000/cors_test.html → click the button → it works.
Now open http://127.0.0.1:3000/cors_test.html → click → BLOCKED in the console.
Same machine, different origin. That's trap (2) from the notes.

Note: curl / Postman never hit CORS — it's a BROWSER rule.
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
    title=f"{get_settings().app_name} — Stage 5 (middleware & CORS)",
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
