import asyncio
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from ..schemas.rates import ConversionRequest, ConversionResult, Currency
from ..services import rates as rate_service

router = APIRouter(prefix="/convert", tags=["convert"])


async def write_audit_log(summary: str):
    await asyncio.sleep(2)  # stand-in for a slow logging service
    print(f"  📝 audit log saved: {summary}")


@router.get("")  # Part 03's GET /convert?amount=&to=
def convert_query(amount: Annotated[float, Query(gt=0)] = 1.0, to: Currency = Currency.usd):
    return {"amount_inr": amount, "to": to, "converted": rate_service.convert(amount, to.value)}


@router.post("", response_model=ConversionResult)  # Part 03's POST /convert
def convert(req: ConversionRequest, bg: BackgroundTasks):
    try:
        converted = rate_service.convert(req.amount, req.to.value)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"no rate for {req.to.value}") from None
    result = ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)
    bg.add_task(write_audit_log, result.summary)  # a plain string, queued; runs AFTER the reply
    return result
