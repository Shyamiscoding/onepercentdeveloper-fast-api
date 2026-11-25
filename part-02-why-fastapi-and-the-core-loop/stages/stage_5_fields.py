"""
STAGE 5 (notes B5) — harden each FIELD inside the body with Field().

Just as Query() constrains a query param, Field() constrains a model field,
with the SAME menu of knobs: gt/ge/lt/le, min_length/max_length, pattern
(regex), description, examples, and more. Field() lives INSIDE the body model
— it is the rule on each key of the JSON object.

Try in /docs:  POST /rates with code="us" -> 422 (fails the pattern) ;
               code="USD" -> ok

Run:  uv run uvicorn stages.stage_5_fields:app --reload
"""

from enum import StrEnum

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Rates API — Stage 5 (fields / Field())")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


# NEW in this stage: per-field rules + docs metadata, stacked together
class RateIn(BaseModel):
    code: str = Field(
        min_length=3, max_length=3, pattern="^[A-Z]{3}$", description="ISO currency code, e.g. USD"
    )
    inr_per_unit: float = Field(gt=0, le=100_000, description="Rate in INR")


class ConversionRequest(BaseModel):
    amount: float
    to: Currency = Currency.usd


@app.get("/rates")  # READ all — the SAME knobs work on a query param
def list_rates(limit: int = Query(default=10, ge=1, le=100, description="How many to return")):
    return dict(list(RATES_TO_INR.items())[:limit])


@app.get("/rates/{code}")  # READ one
def get_rate(code: str):
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates")  # CREATE
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.put("/rates/{code}")  # UPDATE
def update_rate(code: str, rate: RateIn):
    RATES_TO_INR[code] = rate.inr_per_unit
    return rate


@app.delete("/rates/{code}")  # DELETE
def delete_rate(code: str):
    del RATES_TO_INR[code]
    return {"deleted": code}


@app.get("/convert")
def convert(
    amount: float = Query(gt=0, description="Amount in INR"),
    to: Currency = Currency.usd,
):
    return {"amount_inr": amount, "to": to, "converted": round(amount / RATES_TO_INR[to], 2)}


@app.post("/convert")
def create_conversion(req: ConversionRequest):
    converted = round(req.amount / RATES_TO_INR[req.to], 2)
    return {"amount_inr": req.amount, "to": req.to, "converted": converted}
