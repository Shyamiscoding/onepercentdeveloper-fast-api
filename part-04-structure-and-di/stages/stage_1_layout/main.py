"""
STAGE 1 (notes A1) — one file → many: APIRouter and a real layout.

Part 03's main.py, cut into files by job. NOTHING about behaviour changes:
    main.py                    the assembler — creates the app, mounts routers, no logic
    core/config.py             Part 03's Settings, unchanged
    routers/rates.py           THIN — the /rates CRUD and Part 03's /rates/live
    routers/convert.py         THIN — GET and POST /convert
    schemas/rates.py           Part 03's shapes, unchanged (Currency, RateIn, ConversionResult)
    services/rates.py          FAT — the business logic (no FastAPI imports at all)
    services/rate_provider.py  Part 03's live call, moved out of the route

../../src/ is this same app. In Part 05 every stage is a COPY of this folder
plus one new idea, so you can diff to see exactly what each idea added.

/docs looks exactly like Part 03 — users can't tell we reorganised the inside.

Run:  uv run uvicorn stages.stage_1_layout.main:app --reload     (needs .env — see stages/README.md)
"""

from fastapi import FastAPI

from .core.config import settings
from .routers import convert, rates

app = FastAPI(title=f"{settings.app_name} — Stage 1 (layout)")

app.include_router(rates.router)  # mount each mini-app
app.include_router(convert.router)
