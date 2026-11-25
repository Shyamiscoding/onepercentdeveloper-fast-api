"""
STAGE 1 (notes B1) — the whole CRUD resource, NO validation yet.

Five short functions and you can already Create, Read, Update, Delete rates
live in /docs. This is the shape of almost every API you'll build. But it's
naive on purpose: no input checks, every response is a bare 200, and asking
for a missing code crashes with a 500. The next stages harden it, one piece
at a time.

Run:  uv run uvicorn stages.stage_1_crud_raw:app --reload
"""

from fastapi import FastAPI

app = FastAPI(title="Rates API — Stage 1 (raw CRUD)")

# in-memory store — resets every time the server restarts (that's OK for now)
RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


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


# carried over from Part 01 — still unhardened (we fix it in stage 3)
@app.get("/convert")
def convert(amount: float, to: str = "EUR"):
    return {"amount_inr": amount, "to": to, "converted": amount / RATES_TO_INR[to]}
