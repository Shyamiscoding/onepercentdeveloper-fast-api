"""
OnePercent FastAPI course — Part 03: Open the Hood (type hints · Pydantic v2 · async).

This folder is DEDICATED to Part 03. Part 02 lives in its own folder, so the
parts stay clean and easy to share ("this is Part 02, this is Part 03").

------------------------------------------------------------------------------
FIRST TIME (packages come from `uv sync` in fastapi-code/), inside this folder:
    cp .env.example .env

RUN the app:
    uv run uvicorn main:app --reload           # -> http://127.0.0.1:8000/docs

RUN the standalone experiments (no server needed): the script stages, e.g.
    uv run python stages/stage_3_basemodel_pipeline.py
------------------------------------------------------------------------------

This is the FINISHED app (all pieces combined). To teach ONE idea at a time and
run it live, walk the numbered files in ./stages/ (see stages/README.md), then
land here.

What's inside, mapped to the Part 03 notes:
    A1  a type hint only DESCRIBES            -> stages/stage_1_type_hint_passive.py
    A2  Annotated query params                -> stages/stage_2 · /convert, /rates below
    B1  BaseModel parse/validate/coerce       -> stages/stage_3_basemodel_pipeline.py
    B2  validators / computed / serializer    -> stages/stage_4 · RateIn, ConversionResult below
    B3  model_config (extra="forbid", strict) -> stages/stage_5 · RateIn below
    B4  settings from .env (+ a real 3rd-party API)  -> config.py · stages/stage_6 · /rates/live below
    B5  model -> JSON Schema -> OpenAPI               -> stages/stage_7 · /openapi.json
    C2  async def (await httpx) vs plain def          -> stages/stage_8 · /rates/live, /rates/report
    C3  the blocking footgun                          -> stages/stage_8 · /demo/bad-blocking
"""

import time
from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

import httpx
from config import settings  # Part 03 (B4): typed config from env / .env
from fastapi import Cookie, FastAPI, Header, HTTPException, Query, UploadFile, status
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

# Part 03 (B4): the app title comes from validated settings, not a hardcoded string.
app = FastAPI(title=settings.app_name, version="1.0.0")

# ---- in-memory store: resets every restart (fine for now; a real app uses a DB) ----
RATES_TO_INR: dict[str, float] = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


# ---- a value from a FIXED set -> Enum (auto 422 + a dropdown in /docs) ----
class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


# ---- request body shapes, with per-field rules via Field() ----
class RateIn(BaseModel):
    # B3: reject unknown keys instead of silently ignoring them.
    # A typo'd field (e.g. "codee") now fails loudly instead of vanishing.
    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        min_length=3, max_length=3, pattern="^[A-Z]{3}$", description="ISO currency code, e.g. USD"
    )
    inr_per_unit: float = Field(gt=0, le=100_000, description="Rate in INR")

    # B2: clean ONE field BEFORE validation -> " usd " becomes "USD",
    # so lowercase input is accepted and still passes the ^[A-Z]{3}$ pattern.
    @field_validator("code", mode="before")
    @classmethod
    def upper_code(cls, v):
        return v.strip().upper() if isinstance(v, str) else v

    # B2: a rule ACROSS fields -> INR is the base, so its rate must be 1.
    @model_validator(mode="after")
    def base_is_one(self):
        if self.code == "INR" and self.inr_per_unit != 1:
            raise ValueError("INR is the base currency — its rate must be 1")
        return self


class ConversionRequest(BaseModel):
    amount: float = Field(gt=0)  # B2: tighten with a Field rule
    to: Currency = Currency.usd


# ---- OUTPUT shapes. response_model filters what leaves = a security boundary ----
class ConversionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    amount_inr: Decimal
    to: Currency
    converted: Decimal

    # B2: a value DERIVED on output -> shows up in the JSON + in /docs.
    @computed_field
    @property
    def summary(self) -> str:
        return f"{self.amount_inr} INR = {self.converted} {self.to.value}"

    # B2: control how a field is RENDERED in the output JSON.
    @field_serializer("converted")
    def two_dp(self, v: Decimal) -> str:
        return f"{v:.2f}"


# ============================  /rates  — the full CRUD  ============================
# A2: Annotated attaches the validation to the TYPE, leaving `=` for the default.
@app.get("/rates")  # READ all
def list_rates(limit: Annotated[int, Query(ge=1, le=100, description="How many to return")] = 10):
    return dict(list(RATES_TO_INR.items())[:limit])


@app.get("/rates/{code}")  # READ one — 404 instead of a crash
def get_rate(code: str):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates", status_code=status.HTTP_201_CREATED)  # CREATE — 201
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.put("/rates/{code}")  # UPDATE
def update_rate(code: str, rate: RateIn):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    RATES_TO_INR[code] = rate.inr_per_unit
    return rate


@app.delete("/rates/{code}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE — 204
def delete_rate(code: str):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    RATES_TO_INR.pop(code, None)
    return None


# ====================  /convert  — GET (query) + POST (body)  ====================
@app.get("/convert")  # A2: query params hardened with Annotated + Query()
def convert(
    amount: Annotated[float, Query(gt=0, description="Amount in INR")] = 1.0,
    to: Currency = Currency.usd,
):
    return {
        "amount_inr": amount,
        "to": to,
        "converted": round(amount / RATES_TO_INR[to], 2),
    }


@app.post("/convert", response_model=ConversionResult)  # body + response_model
def create_conversion(req: ConversionRequest):
    rate = Decimal(str(RATES_TO_INR[req.to]))
    converted = (Decimal(str(req.amount)) / rate).quantize(Decimal("0.01"))
    return ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)


# ============================  forms & files  ============================
@app.post("/convert/csv")
async def convert_csv(file: UploadFile):
    content = await file.read()
    lines = content.decode().splitlines()
    return {"filename": file.filename, "rows": len(lines)}


# ============================  headers & cookies  ============================
@app.get("/whoami")
def whoami(
    user_agent: str | None = Header(default=None),
    session: str | None = Cookie(default=None),
):
    return {"user_agent": user_agent, "session": session}


# =========  Section C (async vs sync) — the real async use case + the footgun  =========
# A live rate comes from a 3rd-party API over the network = a real WAIT. That wait is
# exactly WHY this handler is `async`: while we await the provider, the event loop keeps
# serving other requests. Get a free key (App ID) at https://openexchangerates.org and set it in .env
# as RATE_API_KEY. (httpx ships with fastapi[standard] — nothing extra to install.)


# ✅ C2 — the correct async shape: await an async library (httpx) for the network wait.
#        This is where config.py's rate_api_url + rate_api_key are actually used.
@app.get("/rates/live")
async def live_rate(to: Currency = Currency.usd):
    params = {"app_id": settings.rate_api_key}
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{settings.rate_api_url}/api/latest.json", params=params)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="rate provider unavailable")
    rates = res.json().get("rates", {})
    inr_per_usd = rates.get("INR")  # base=USD -> INR per 1 USD
    to_per_usd = rates.get(to.value)  # units of `to` per 1 USD
    if inr_per_usd is None or not to_per_usd:
        raise HTTPException(status_code=502, detail="rate unavailable for this currency")
    return {
        "to": to.value,
        "inr_per_unit": round(inr_per_usd / to_per_usd, 2),  # INR per 1 unit of `to`
        "source": "live",
    }


# ✅ C2 — only a SYNC library available? use plain `def`: FastAPI runs it in a THREAD POOL,
#        so the blocking call stays OFF the event loop and can't freeze other requests.
@app.get("/rates/report")
def rates_report():
    time.sleep(1)  # stand-in for a slow SYNC library (e.g. building a PDF)
    return {"rows": len(RATES_TO_INR), "rates": RATES_TO_INR}


# ❌ C3 — the FOOTGUN: the same idea done WRONG. A blocking call inside `async def` freezes
# the single event-loop thread, so EVERY concurrent request stalls — not just this one.
# To SEE it: hit /demo/bad-blocking in one tab, then hit /rates or /convert in another —
# the second one hangs for the full 3s. (The fix is /rates/live above: await, don't block.)
@app.get("/demo/bad-blocking")
async def bad_blocking():
    time.sleep(3)  # ❌ blocks the whole loop (should be: await asyncio.sleep)
    return {
        "ok": True,
        "note": "this blocked the ENTIRE server for 3s — never do this in async def",
    }
