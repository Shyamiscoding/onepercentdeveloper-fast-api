"""/rates — same endpoints as Part 04's layout, but they ASK for what they
need instead of building it."""

from fastapi import APIRouter, HTTPException, status

from ..core.deps import FilterDep, PageParams, ProviderDep
from ..schemas.rates import Currency, RateIn, RatePage
from ..services import rates as rate_service
from ..services.rate_provider import RateProviderError

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("", response_model=RatePage)
def list_rates(page: PageParams):  # 1) a function dependency
    items, total = rate_service.list_rates(**page)
    return RatePage(items=items, total=total, **page)


@router.get("/search", response_model=RatePage)
def search_rates(f: FilterDep, page: PageParams):  # 2) a class dependency + pagination reused
    items, total = rate_service.list_rates(min_rate=f.min_rate, max_rate=f.max_rate, **page)
    return RatePage(items=items, total=total, **page)


@router.get("/live")  # before /{code}, or "live" would match {code}
async def live_rate(provider: ProviderDep, to: Currency = Currency.usd):
    # 3) the route only says "I need a rate provider". FastAPI builds settings → provider → calls us.
    try:
        rates = await provider.inr_rates()
    except RateProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"to": to.value, "inr_per_unit": round(rates[to.value], 2), "source": "live"}


@router.get("/{code}")
def get_rate(code: str):
    rate = rate_service.get_rate(code)
    if rate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
    return {"code": code.upper(), "inr_per_unit": rate}


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
