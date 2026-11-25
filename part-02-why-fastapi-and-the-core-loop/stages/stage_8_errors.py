"""
STAGE 8 (notes B8) — error handling: the 404 stage 1 was missing.

Stage 1's get_rate did RATES_TO_INR[code] -> KeyError -> an ugly 500 when the
code wasn't there. For EXPECTED problems like "not found", raise an
HTTPException with the right code. (Validation errors still raise the automatic
422 for free — no code needed.)

Run:  uv run uvicorn stages.stage_8_errors:app --reload
"""

from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Rates API — Stage 8 (errors / HTTPException)")

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


class ConversionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    amount_inr: Decimal
    to: Currency
    converted: Decimal


class SubscriberIn(BaseModel):
    email: EmailStr
    password: str


class SubscriberPublic(BaseModel):
    id: UUID
    email: EmailStr


@app.get("/rates")
def list_rates(limit: int = Query(default=10, ge=1, le=100)):
    return dict(list(RATES_TO_INR.items())[:limit])


# NEW in this stage: a clean 404 instead of a 500 crash
@app.get("/rates/{code}")
def get_rate(code: str):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found for this")
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates", status_code=status.HTTP_201_CREATED)
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.put("/rates/{code}")
def update_rate(code: str, rate: RateIn):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    RATES_TO_INR[code] = rate.inr_per_unit
    return rate


@app.delete("/rates/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rate(code: str):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    RATES_TO_INR.pop(code, None)
    return None


@app.get("/convert")
def convert(amount: float = Query(gt=0), to: Currency = Currency.usd):
    return {"amount_inr": amount, "to": to, "converted": round(amount / RATES_TO_INR[to], 2)}


@app.post("/convert", response_model=ConversionResult)
def create_conversion(req: ConversionRequest):
    rate = Decimal(str(RATES_TO_INR[req.to]))
    converted = (Decimal(str(req.amount)) / rate).quantize(Decimal("0.01"))
    return ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)


@app.post("/subscribers", response_model=SubscriberPublic, status_code=201)
def create_subscriber(sub: SubscriberIn):
    return SubscriberPublic(id=uuid4(), email=sub.email)
