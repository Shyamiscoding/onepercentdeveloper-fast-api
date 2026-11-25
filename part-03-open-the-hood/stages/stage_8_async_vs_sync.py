"""
STAGE 8 (notes C2 + C3) — async def vs def, and the blocking footgun.

- /rates/live        : async def + await httpx -> correct for I/O (a real wait)
- /rates/report      : plain def               -> FastAPI runs sync work in a THREAD POOL
- /demo/bad-blocking : the FOOTGUN — time.sleep inside async def freezes the WHOLE loop

To SEE the footgun: hit /demo/bad-blocking in one browser tab, then hit
/rates/report in another — it hangs for the full 3s because the event loop is
frozen. One blocking call stalled every request on the worker.

Run:  uv run uvicorn stages.stage_8_async_vs_sync:app --reload
"""

import time
from enum import StrEnum

import httpx
from config import settings
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Rates API — Stage 8 (async vs sync)")

RATES_TO_INR = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


# ✅ async def + await: the correct shape for a network wait (I/O-bound)
@app.get("/rates/live")
async def live_rate(to: Currency = Currency.usd):
    params = {"app_id": settings.rate_api_key}
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{settings.rate_api_url}/api/latest.json", params=params)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="rate provider unavailable")
    rates = res.json().get("rates", {})
    inr_per_usd = rates.get("INR")
    to_per_usd = rates.get(to.value)  # units of `to` per 1 USD
    if inr_per_usd is None or not to_per_usd:
        raise HTTPException(status_code=502, detail="rate unavailable for this currency")
    return {
        "to": to.value,
        "inr_per_unit": round(inr_per_usd / to_per_usd, 2),  # INR per 1 unit of `to`
        "source": "live",
    }


# ✅ plain def: sync work runs in a thread pool, OFF the event loop — safe
@app.get("/rates/report")
def rates_report():
    time.sleep(1)  # stand-in for a slow SYNC library (e.g. building a PDF)
    return {"rows": len(RATES_TO_INR), "rates": RATES_TO_INR}


# ❌ the FOOTGUN: a blocking call inside async def freezes EVERY request on the worker
@app.get("/demo/bad-blocking")
async def bad_blocking():
    time.sleep(3)  # ❌ should be: await asyncio.sleep(3)
    return {
        "ok": True,
        "note": "this blocked the ENTIRE server for 3s — never do this in async def",
    }
