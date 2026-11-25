"""
Stage 1 demo only — per-request caching, and THE RULE. Not carried into stage 2.

    If FastAPI calls it, it can use Depends. If YOU call it, pass plain params.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from ..core.deps import PageParams, ProviderDep
from ..services.rate_provider import RateProvider

router = APIRouter(prefix="/demo")


# ── 4) asked for twice, runs ONCE per request ──────────────────────────
@router.get("/cache", tags=["with DI"])
def cache_demo(a: PageParams, b: PageParams):
    # pagination() prints ONCE in the terminal — FastAPI caches a dependency per request
    return {"same_object": a is b}


# ── 5) THE RULE ────────────────────────────────────────────────────────
def describe_provider(provider: ProviderDep) -> str:  # a helper that ASKS via Depends
    return f"live rates come from {provider.settings.rate_api_url}"


@router.get("/wrong-call", tags=["the rule"])
def wrong_call():
    try:
        return {"result": describe_provider()}  # ❌ WE call it — FastAPI never sees this call
    except TypeError as exc:
        return {
            "error": f"TypeError: {exc}",
            "why": "Depends is only a note FOR FastAPI. When you call the function yourself, "
            "Python just sees a missing argument. (With the older `= Depends(...)` default "
            "style it's worse: no error here, then an AttributeError on the Depends marker.)",
            "fix": "see /demo/right-call-1 and /demo/right-call-2",
        }


@router.get("/right-call-1", tags=["the rule"])
def right_call_1(
    text: Annotated[str, Depends(describe_provider)],
):  # ✅ fix A: FastAPI calls the helper
    return {"result": text}


def describe_provider_plain(provider: RateProvider) -> str:  # ✅ fix B: a plain helper, no Depends
    return f"live rates come from {provider.settings.rate_api_url}"


@router.get("/right-call-2", tags=["the rule"])
def right_call_2(provider: ProviderDep):
    return {"result": describe_provider_plain(provider)}  # the route got it, the route passes it on
