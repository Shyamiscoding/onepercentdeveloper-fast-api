"""/rates — the public reads. Writes moved to routers/admin.py; one guarded route stays here."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from ..core.deps import FilterDep, PageParams, ProviderDep, require_api_key
from ..schemas.rates import Currency, RatePage
from ..services import rates as rate_service
from ..services.rate_provider import RateProvider, RateProviderError

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("", response_model=RatePage)
def list_rates(page: PageParams):
    items, total = rate_service.list_rates(**page)
    return RatePage(items=items, total=total, **page)


@router.get("/search", response_model=RatePage)
def search_rates(f: FilterDep, page: PageParams):
    items, total = rate_service.list_rates(min_rate=f.min_rate, max_rate=f.max_rate, **page)
    return RatePage(items=items, total=total, **page)


@router.get("/live")  # before /{code}, or "live" would match {code}
async def live_rate(provider: ProviderDep, to: Currency = Currency.usd):
    try:
        rates = await provider.inr_rates()
    except RateProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return {"to": to.value, "inr_per_unit": round(rates[to.value], 2), "source": "live"}


async def sync_in_background(provider: RateProvider):
    try:
        rates = await rate_service.sync_from_provider(provider)
    except RateProviderError as exc:
        print(f"  ⚠ background sync failed: {exc}")  # nobody is waiting to see an error
        return
    print(f"  🔄 rates synced in the background: {rates}")


# ONE ROUTE guarded: every call spends our free API quota (~1,000 calls a month)
@router.post("/sync", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(require_api_key)])
def sync_rates(provider: ProviderDep, bg: BackgroundTasks):
    # safe to hand the provider over: its client lives per PROCESS (stage 4).
    # With stage 2's per-request client it would already be CLOSED when the task runs.
    bg.add_task(sync_in_background, provider)
    return {"accepted": True, "check": "GET /rates in a moment"}  # 202 = "got it, working on it"


@router.get("/{code}")
def get_rate(code: str):
    rate = rate_service.get_rate(code)
    if rate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "rate not found")
    return {"code": code.upper(), "inr_per_unit": rate}
