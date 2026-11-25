"""Request/response SHAPES only — Part 03's models, moved into their own file. Nothing changed."""

from decimal import Decimal
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


class RateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    inr_per_unit: float = Field(gt=0, le=100_000)

    @field_validator("code", mode="before")
    @classmethod
    def upper_code(cls, v):
        return v.strip().upper() if isinstance(v, str) else v

    @model_validator(mode="after")
    def base_is_one(self):
        if self.code == "INR" and self.inr_per_unit != 1:
            raise ValueError("INR is the base currency — its rate must be 1")
        return self


class ConversionRequest(BaseModel):
    amount: float = Field(gt=0)
    to: Currency = Currency.usd


class ConversionResult(BaseModel):
    amount_inr: Decimal
    to: Currency
    converted: Decimal

    @computed_field
    @property
    def summary(self) -> str:
        return f"{self.amount_inr} INR = {self.converted} {self.to.value}"

    @field_serializer("converted")
    def two_dp(self, v: Decimal) -> str:
        return f"{v:.2f}"


class RatePublic(BaseModel):
    code: str
    inr_per_unit: float


class RatePage(BaseModel):  # the list envelope that pagination needs
    items: list[RatePublic]
    total: int
    limit: int
    offset: int
