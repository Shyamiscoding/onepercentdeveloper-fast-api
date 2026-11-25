"""
STAGE 3 (notes A3) — where a dependency applies: route, router, or whole app.

Stage 2's folder, plus:
    core/config.py      + admin_api_key ("secret" by default, from .env)
    core/deps.py        + require_api_key (a guard) and log_request
    services/rates.py   + sync_from_provider: refresh our rates from the live provider
    routers/admin.py    NEW — the writes (POST/PUT/DELETE), moved out of routers/rates.py
    routers/rates.py    the reads stay public; + POST /rates/sync
    (stage 2's yield demo is gone)

The three scopes:
    WHOLE APP   log_request runs for EVERY request         FastAPI(dependencies=[...])  — below
    ONE ROUTER  require_api_key guards all of /admin/rates  APIRouter(dependencies=[...]) — admin.py
    ONE ROUTE   require_api_key guards only POST /rates/sync                              — rates.py

Why guard /rates/sync? It calls the LIVE provider, and the free plan allows
~1,000 calls a month. Left open, anyone could burn our quota in a minute.

Try in /docs: /admin/rates and /rates/sync answer 401 until you send the header
x-api-key: secret   (the real login arrives in Part 07).

Run:  uv run uvicorn stages.stage_3_scoped_deps.main:app --reload     (needs .env — see stages/README.md)
"""

from fastapi import Depends, FastAPI

from .core.config import get_settings
from .core.deps import log_request
from .routers import admin, convert, rates

app = FastAPI(
    title=f"{get_settings().app_name} — Stage 3 (scoped dependencies)",
    dependencies=[Depends(log_request)],
)  # WHOLE APP

app.include_router(rates.router)
app.include_router(admin.router)
app.include_router(convert.router)
