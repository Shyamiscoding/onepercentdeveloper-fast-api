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

from fastapi import FastAPI

from .core.config import settings
from .routers import convert, rates

app = FastAPI(title=settings.app_name)

app.include_router(rates.router)  # mount each mini-app
app.include_router(convert.router)
