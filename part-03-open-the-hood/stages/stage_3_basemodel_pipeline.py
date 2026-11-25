"""
STAGE 3 (notes B1) — BaseModel = parse -> validate -> coerce -> serialize.

A Pydantic model is not a fancy dict. `model_validate` runs a pipeline on raw
input; `model_dump` / `model_dump_json` send it back out. Run this to SEE the
string "83.0" become a real float (that's COERCION, the lax default).

Run:  uv run python stages/stage_3_basemodel_pipeline.py
"""

from pydantic import BaseModel


class Rate(BaseModel):  # a tiny stand-in with the SAME two fields as RateIn
    code: str
    inr_per_unit: float


raw = {"code": "USD", "inr_per_unit": "83.0"}  # untrusted input (text, like a request)

r = Rate.model_validate(raw)
#   1) PARSE    -> read the dict, match keys to fields (code, inr_per_unit)
#   2) VALIDATE -> is code a str? is inr_per_unit a number? (reject if not)
#   3) COERCE   -> the string "83.0" becomes a real float 83.0

print("STAGE 3 — the BaseModel pipeline")
print(f"   inr_per_unit = {r.inr_per_unit!r}   (the string '83.0' was COERCED to a float)")
print(f"   model_dump()      = {r.model_dump()}        # 4) SERIALIZE -> dict")
print(f"   model_dump_json() = {r.model_dump_json()}   # 4) SERIALIZE -> JSON text")
