"""Stage 6 demo only — the SAME conversion with the audit log done inline, so the client waits."""

import time

from fastapi import APIRouter

from ..schemas.rates import ConversionRequest, ConversionResult
from ..services import rates as rate_service

router = APIRouter(prefix="/demo", tags=["background demo"])


@router.post("/convert-slow", response_model=ConversionResult)
def convert_slow(req: ConversionRequest):
    converted = rate_service.convert(req.amount, req.to.value)
    result = ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)
    time.sleep(2)  # the log written BEFORE replying — don't do this
    print(f"  📝 audit log saved: {result.summary}")
    return result
