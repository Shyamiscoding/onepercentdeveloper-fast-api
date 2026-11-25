"""
STAGE 4 (notes B2) — validators, computed fields & serializers.

Field() covers simple rules. For custom logic Pydantic gives you four hooks:
  @field_validator  — clean/check ONE field   (here: uppercase the code)
  @model_validator  — a rule ACROSS fields     (here: INR base rate must be 1)
  @computed_field   — a value DERIVED on output (here: summary)
  @field_serializer — control how a field RENDERS (here: converted -> "100.00")

Try in /docs:  POST /rates {code:"usd", inr_per_unit:90} -> stored as "USD" ;
               POST /convert {amount:8300, to:"USD"} -> see `summary` + 2dp `converted`
Run:  uv run uvicorn stages.stage_4_validators_computed:app --reload
"""

from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import FastAPI, status
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

app = FastAPI(title="Rates API — Stage 4 (validators/computed/serializer)")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


class RateIn(BaseModel):
    code: str = Field(min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    inr_per_unit: float = Field(gt=0, le=100_000)

    @field_validator("code", mode="before")  # clean ONE field (raw input)
    @classmethod
    def upper_code(cls, v):
        return v.strip().upper() if isinstance(v, str) else v

    @model_validator(mode="after")  # a rule ACROSS fields
    def base_is_one(self):
        if self.code == "INR" and self.inr_per_unit != 1:
            raise ValueError("INR is the base currency — its rate must be 1")
        return self


class ConversionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(gt=0)
    to: Currency = Currency.usd


class ConversionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    amount_inr: Decimal
    to: Currency
    converted: Decimal

    @computed_field  # DERIVED on output
    @property
    def summary2(self) -> str:
        return f"{self.amount_inr} INR = {self.converted} {self.to.value}"

    @field_serializer("converted")  # control the OUTPUT rendering
    def two_dp(self, v: Decimal) -> str:
        return f"{v:.2f}"


@app.post("/rates", status_code=status.HTTP_201_CREATED)
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.post("/convert", response_model=ConversionResult)
def create_conversion(req: ConversionRequest):
    rate = Decimal(str(RATES_TO_INR[req.to]))
    converted = (Decimal(str(req.amount)) / rate).quantize(Decimal("0.01"))
    return ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)
