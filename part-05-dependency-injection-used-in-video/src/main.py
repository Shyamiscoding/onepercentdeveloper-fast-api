"""
OnePercent FastAPI course — Part 04, the FINISHED app: Part 03's currency API, given a shape.

Part 03's main.py, cut into files by job. NOTHING about behaviour changes:
    main.py                    the assembler — creates the app, mounts routers, no logic
    core/config.py             Part 03's Settings, unchanged
    routers/rates.py           THIN — the /rates CRUD and Part 03's /rates/live
    routers/convert.py         THIN — GET and POST /convert
    schemas/rates.py           Part 03's shapes, unchanged (Currency, RateIn, ConversionResult)
    services/rates.py          FAT — the business logic (no FastAPI imports at all)
    services/rate_provider.py  Part 03's live call, moved out of the route

/docs looks exactly like Part 03 — users can't tell we reorganised the inside.
Every route still builds what it needs itself. Part 05 fixes that: dependency injection.

Run (from part-04-structure-and-di/):
    cp ../part-03-open-the-hood/.env .env     # once — it has your RATE_API_KEY
    uv run uvicorn src.main:app --reload      # → http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
from fastapi import Depends, FastAPI

from .core.config import settings
from .core.deps import log_request
from .routers import convert, health, rates


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP: opening ONE http client for the whole app")
    app.state.http = httpx.AsyncClient(timeout=10)
    app.state.started_at = datetime.now(UTC)  # for the /uptime proof
    yield  # ── the app runs here
    print("SHUTDOWN: closing the http client")
    await app.state.http.aclose()


app = FastAPI(
    title=settings.app_name, dependencies=[Depends(log_request)], lifespan=lifespan
)


import time

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware


@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)  # ── the route runs here
    response.headers["shyam-process-time-ms"] = (
        f"{(time.perf_counter() - start) * 1000:.1f}"
    )
    return response


# added LAST -> outermost: it answers the browser's preflight before anything else
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # exact origin: scheme + host + port
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "shyam-process-time-ms"
    ],  # custom headers are hidden from JS unless exposed
)

app.include_router(rates.router)  # mount each mini-app
app.include_router(convert.router)
app.include_router(health.router)
