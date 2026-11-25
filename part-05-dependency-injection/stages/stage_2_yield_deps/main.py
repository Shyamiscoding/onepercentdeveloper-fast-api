"""
STAGE 2 (notes A2) — yield dependencies: setup before, teardown after.

Stage 1's folder, plus:
    core/deps.py               + get_http_client: a yield dependency, ONE client per REQUEST,
                                 closed after the response. get_rate_provider now asks for it.
    services/rate_provider.py  RateProvider is handed the client instead of opening its own
    routers/demo.py            demo — a FakeSession that prints its whole lifecycle
                               (stage 1's before_di and rule demos are gone)

Nothing in routers/rates.py changed: the route still just asks for a provider.
    GET /rates/live            watch the terminal: [http] client OPEN … CLOSED
    GET /demo/session/USD      OPEN → route → COMMIT → CLOSE
    GET /demo/error            OPEN → route → ROLLBACK → CLOSE (cleanup still runs)
    GET /demo/nested           two yield deps: teardown runs in REVERSE order

Run:  uv run uvicorn stages.stage_2_yield_deps.main:app --reload     (needs .env — see stages/README.md)
"""

from fastapi import FastAPI

from .core.config import get_settings
from .routers import convert, demo, rates

app = FastAPI(title=f"{get_settings().app_name} — Stage 2 (yield dependencies)")

app.include_router(rates.router)
app.include_router(convert.router)
app.include_router(demo.router)
