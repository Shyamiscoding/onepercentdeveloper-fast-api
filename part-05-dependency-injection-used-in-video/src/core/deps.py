from typing import Annotated

from fastapi import Depends, Query


def pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    print("  pagination() called")
    return {"limit": limit, "offset": offset}


PageParams = Annotated[dict, Depends(pagination)]


import httpx


async def get_http_client():
    async with httpx.AsyncClient(timeout=10) as client:  # ── setup
        print("  [http] client OPEN")
        try:
            yield client  # ── the route runs here
        finally:
            print(
                "  [http] client CLOSED"
            )  # ── teardown: after the response, even on error


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]


from ..services.rate_provider import RateProvider
from .config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_rate_provider(settings: SettingsDep, client: HttpClientDep) -> RateProvider:
    print("  get_rate_provider() called")
    return RateProvider(settings, client)


ProviderDep = Annotated[RateProvider, Depends(get_rate_provider)]


from fastapi import Header, HTTPException, Request, status


def require_api_key(
    settings: SettingsDep, x_api_key: Annotated[str | None, Header()] = None
):
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing or bad x-api-key")


def log_request(request: Request):
    print(f"  [app-level] {request.method} {request.url.path}")


from fastapi import Request


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http  # lifespan opened it; every request shares it


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
