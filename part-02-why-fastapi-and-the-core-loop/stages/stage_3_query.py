"""
STAGE 3 (notes B3) — harden the QUERY with Query().

Any function argument NOT in the path is a query parameter (the ?key=value).
Query() lets you validate it. Query(gt=0) means /convert?amount=-5 is now an
automatic 422 — the hand-written 400 from Part 01 is now one word.

Query() also gives min_length, max_length, pattern (regex), alias, and
list/multiple values — the same menu you'll see for Field() in stage 5.

Run:  uv run uvicorn stages.stage_3_query:app --reload
"""

from enum import StrEnum

from fastapi import FastAPI, Query

app = FastAPI(title="Rates API — Stage 3 (query / Query())")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


@app.get("/rates")  # READ all
def list_rates():
    return RATES_TO_INR


@app.get("/rates/{code}")  # READ one
def get_rate(code: str):
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates")  # CREATE
def create_rate(code: str, inr_per_unit: float):
    RATES_TO_INR[code] = inr_per_unit
    return {"code": code, "inr_per_unit": inr_per_unit}


@app.put("/rates/{code}")  # UPDATE
def update_rate(code: str, inr_per_unit: float):
    RATES_TO_INR[code] = inr_per_unit
    return {"code": code, "inr_per_unit": inr_per_unit}


@app.delete("/rates/{code}")  # DELETE
def delete_rate(code: str):
    del RATES_TO_INR[code]
    return {"deleted": code}


# NEW in this stage: Query(gt=0) -> negative amounts are an automatic 422
@app.get("/convert")
def convert(
    amount: float = Query(gt=0, description="Amount in INR"),
    to: Currency = Currency.usd,
):
    return {
        "amount_inr": amount,
        "to": to,
        "converted": round(amount / RATES_TO_INR[to], 2),
    }
