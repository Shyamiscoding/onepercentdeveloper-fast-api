from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from ..schemas.rates import ConversionRequest, ConversionResult, Currency
from ..services import rates as rate_service

router = APIRouter(prefix="/convert", tags=["convert"])


@router.get("")  # Part 03's GET /convert?amount=&to=
def convert_query(amount: Annotated[float, Query(gt=0)] = 1.0, to: Currency = Currency.usd):
    return {"amount_inr": amount, "to": to, "converted": rate_service.convert(amount, to.value)}


@router.post("", response_model=ConversionResult)  # Part 03's POST /convert
def convert(req: ConversionRequest):
    # thin: hand the work to the service, translate its error into HTTP
    try:
        converted = rate_service.convert(req.amount, req.to.value)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"no rate for {req.to.value}") from None
    return ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)
