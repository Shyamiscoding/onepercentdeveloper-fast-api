"""
STAGE 2 (notes B2) — harden the PATH with an Enum.

When a value must come from a FIXED set, type it as an Enum. FastAPI now
accepts only USD / EUR / GBP, auto-rejects anything else with a 422, and
/docs renders a dropdown.

Note on route order: declare FIXED routes before PARAMETERIZED ones. If
/rates/{code} came before a fixed /rates/latest, FastAPI would read "latest"
as a code. First match wins.

Run:  uv run uvicorn stages.stage_2_path_enum:app --reload
"""

from enum import StrEnum

from fastapi import FastAPI

app = FastAPI(title="Rates API — Stage 2 (path / Enum)")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


# NEW in this stage: a value from a fixed set -> Enum
class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


@app.get("/rates")  # READ all
def list_rates():
    return RATES_TO_INR


# READ one: path typed as the Enum -> only USD/EUR/GBP (bad codes auto-422 + a /docs dropdown)
@app.get("/rates/{code}")  # READ one
def get_rate(code: Currency):
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


# writes keep code: str on purpose — so you can still add brand-new currencies
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


# the Enum constrains /convert's target to the three known currencies
@app.get("/convert")
def convert(amount: float, to: Currency = Currency.usd):
    return {"amount_inr": amount, "to": to, "converted": amount / RATES_TO_INR[to]}
