"""
STAGE 7 (notes B5) — a model describes itself as JSON Schema.

Every Pydantic model can emit JSON Schema. FastAPI collects every model's schema
into one OpenAPI document, which /docs renders. One declaration -> validation AND
the public contract. Run this to see the schema your model generates.

Run:  uv run python stages/stage_7_json_schema.py
"""

import json
from enum import StrEnum

from pydantic import BaseModel, Field


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


class ConversionRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount in INR")
    to: Currency = Currency.usd


print("STAGE 7 — model_json_schema()")
print(json.dumps(ConversionRequest.model_json_schema(), indent=2))
# note: 'amount' is required; 'to' has a default, so it is NOT in "required".
