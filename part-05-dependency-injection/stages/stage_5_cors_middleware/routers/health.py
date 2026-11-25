"""/uptime — proof that startup ran exactly once, and which rates it loaded."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/uptime")
def uptime(request: Request):
    started = request.app.state.started_at
    return {
        "started_at": started.isoformat(),
        "seconds": round((datetime.now(UTC) - started).total_seconds(), 1),
        "rates_source": request.app.state.rates_source,
    }  # "live" or "fallback"
