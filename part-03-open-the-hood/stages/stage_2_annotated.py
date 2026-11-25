"""
STAGE 2 (notes A2) — Annotated: attach the rule TO the type (the 2026 way).

Part 02 wrote `amount: float = Query(gt=0)`. Here we move the rule into the type
with `Annotated[float, Query(gt=0)]`, which frees the `=` for a real default and
lets us NAME a rule once (AmountInr) and reuse it. Annotated itself enforces
nothing — it just carries the rule; Pydantic / FastAPI still do the validating.

Try in /docs:  GET /convert?amount=-5  -> 422 ;  amount=8300 -> ok
Run:  uv run uvicorn stages.stage_2_annotated:app --reload
"""

from enum import StrEnum
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Rates API — Stage 2 (Annotated)")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


# NEW: name a validated rule ONCE, reuse it anywhere it's needed
AmountInr = Annotated[float, Field(gt=0, description="Amount in INR")]


class ConversionRequest(BaseModel):
    amount: AmountInr  # was: amount: float
    to: Currency = Currency.usd


@app.get("/rates")  # NEW: Annotated on a query param
def list_rates(limit: Annotated[int, Query(ge=1, le=100)] = 10):
    return dict(list(RATES_TO_INR.items())[:limit])


@app.get("/convert")  # NEW: the rule rides on the TYPE, default stays on `=`
def convert(
    amount: Annotated[float, Query(gt=0, description="Amount in INR")] = 1.0,
    to: Currency = Currency.usd,
):
    return {"amount_inr": amount, "to": to, "converted": round(amount / RATES_TO_INR[to], 2)}


@app.post("/convert")  # the AmountInr rule is reused here via the model
def create_conversion(req: ConversionRequest):
    return {
        "amount_inr": req.amount,
        "to": req.to,
        "converted": round(req.amount / RATES_TO_INR[req.to], 2),
    }
