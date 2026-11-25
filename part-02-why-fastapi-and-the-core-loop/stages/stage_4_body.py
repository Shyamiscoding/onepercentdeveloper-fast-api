"""
STAGE 4 (notes B4) — real writes take a BODY (a Pydantic BaseModel).

Stage 1's create/update took loose ?code=&inr_per_unit= query params. Fine for
a toy, wrong for real writes. Structured data (POST, PUT) belongs in the JSON
request body, and you declare its shape as a Pydantic model. One type hint
(rate: RateIn) and FastAPI parses the JSON, validates it, and hands you a clean
Python object.

Run:  uv run uvicorn stages.stage_4_body:app --reload
"""

from enum import StrEnum

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Rates API — Stage 4 (body / BaseModel)")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


# NEW in this stage: body shapes declared as Pydantic models
class RateIn(BaseModel):
    code: str
    inr_per_unit: float


class ConversionRequest(BaseModel):
    amount: float
    to: Currency = Currency.usd


@app.get("/rates")  # READ all
def list_rates():
    return RATES_TO_INR


@app.get("/rates/{code}")  # READ one
def get_rate(code: str):
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates")  # CREATE — now takes a validated JSON body
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.put("/rates/{code}")  # UPDATE — body too
def update_rate(code: str, rate: RateIn):
    RATES_TO_INR[code] = rate.inr_per_unit
    return rate


@app.delete("/rates/{code}")  # DELETE
def delete_rate(code: str):
    del RATES_TO_INR[code]
    return {"deleted": code}


@app.get("/convert")  # GET still uses query params
def convert(
    amount: float = Query(gt=0, description="Amount in INR"),
    to: Currency = Currency.usd,
):
    return {"amount_inr": amount, "to": to, "converted": round(amount / RATES_TO_INR[to], 2)}


# same path, different method: POST /convert takes a JSON body
@app.post("/convert")
def create_conversion(req: ConversionRequest):
    converted = round(req.amount / RATES_TO_INR[req.to], 2)
    return {"amount_inr": req.amount, "to": req.to, "converted": converted}
