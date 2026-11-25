"""
STAGE 6 (notes B6) — shape the OUTPUT with response_model (a security boundary).

Input is shaped; now shape what LEAVES. response_model makes FastAPI validate,
filter, and serialise whatever you return to match it. The 1% insight: it is
security, not just formatting. If the response model has no password field,
even returning the whole object can't leak it.

Run:  uv run uvicorn stages.stage_6_response_model:app --reload
"""

from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import FastAPI, Query
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Rates API — Stage 6 (response_model)")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


class RateIn(BaseModel):
    code: str = Field(
        min_length=3, max_length=3, pattern="^[A-Z]{3}$", description="ISO currency code, e.g. USD"
    )
    inr_per_unit: float = Field(gt=0, le=100_000, description="Rate in INR")


class ConversionRequest(BaseModel):
    amount: float
    to: Currency = Currency.usd


# NEW in this stage: OUTPUT models
class ConversionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    amount_inr: Decimal
    to: Currency
    converted: Decimal


class SubscriberIn(BaseModel):
    email: EmailStr
    password: str  # comes IN


class SubscriberPublic(BaseModel):
    id: UUID
    email: EmailStr  # NO password -> can never leak


@app.get("/rates")
def list_rates(limit: int = Query(default=10, ge=1, le=100)):
    return dict(list(RATES_TO_INR.items())[:limit])


@app.get("/rates/{code}")
def get_rate(code: str):
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates")
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.put("/rates/{code}")
def update_rate(code: str, rate: RateIn):
    RATES_TO_INR[code] = rate.inr_per_unit
    return rate


@app.delete("/rates/{code}")
def delete_rate(code: str):
    del RATES_TO_INR[code]
    return {"deleted": code}


@app.get("/convert")
def convert(amount: float = Query(gt=0), to: Currency = Currency.usd):
    return {"amount_inr": amount, "to": to, "converted": round(amount / RATES_TO_INR[to], 2)}


@app.post("/convert", response_model=ConversionResult)
def create_conversion(req: ConversionRequest):
    rate = Decimal(str(RATES_TO_INR[req.to]))
    converted = (Decimal(str(req.amount)) / rate).quantize(Decimal("0.01"))
    return ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)


@app.post("/subscribers", response_model=SubscriberPublic)
def create_subscriber(sub: SubscriberIn):
    # even though we build it from the incoming data, the response_model strips
    # everything that isn't id + email -> the password never goes back out.
    return SubscriberPublic(id=uuid4(), email=sub.email)
