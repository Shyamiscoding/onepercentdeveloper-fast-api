"""/admin/rates — the writes, moved out of routers/rates.py. ONE ROUTER guard covers all of them."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.deps import require_api_key
from ..schemas.rates import RateIn
from ..services import rates as rate_service

router = APIRouter(
    prefix="/admin/rates", tags=["admin"], dependencies=[Depends(require_api_key)]
)  # runs before EVERY route below


@router.post("", status_code=status.HTTP_201_CREATED)
def create_rate(rate: RateIn):
    rate_service.set_rate(rate.code, rate.inr_per_unit)
    return rate


@router.put("/{code}")
def update_rate(code: str, rate: RateIn):
    if rate_service.get_rate(code) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
    rate_service.set_rate(code, rate.inr_per_unit)
    return rate


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rate(code: str):
    if not rate_service.delete_rate(code):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
