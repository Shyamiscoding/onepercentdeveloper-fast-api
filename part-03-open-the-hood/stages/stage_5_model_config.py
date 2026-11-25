"""
STAGE 5 (notes B3) — model_config: lax vs strict, and extra="forbid".

model_config is a Pydantic dial on the WHOLE model. Default is LAX (it coerces).
strict=True refuses to coerce; extra="forbid" rejects unknown keys. Run this to
SEE all three. (In a FastAPI request, each failure surfaces as a 422.)

Run:  uv run python stages/stage_5_model_config.py
"""

from pydantic import BaseModel, ConfigDict, ValidationError


class LaxRate(BaseModel):  # the default — coerces
    code: str
    inr_per_unit: float


class StrictRate(BaseModel):  # same fields, but strict — no coercion
    model_config = ConfigDict(strict=True)
    code: str
    inr_per_unit: float


class NoExtraRate(BaseModel):  # reject unknown keys
    model_config = ConfigDict(extra="forbid")
    code: str
    inr_per_unit: float


print("STAGE 5 — model_config")

lax = LaxRate.model_validate({"code": "USD", "inr_per_unit": "83.0"})
print(f"   LAX     : '83.0' -> {lax.inr_per_unit!r}   (coerced)")

try:
    StrictRate.model_validate({"code": "USD", "inr_per_unit": "83.0"})
except ValidationError:
    print("   STRICT  : '83.0' REJECTED (strict = no coercion)")

try:
    NoExtraRate.model_validate({"code": "USD", "inr_per_unit": 83.0, "codee": "typo"})
except ValidationError:
    print("   FORBID  : unknown key 'codee' REJECTED (would've vanished silently in lax)")
