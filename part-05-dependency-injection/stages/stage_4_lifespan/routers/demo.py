"""Stage 4 demo only — proof that every request gets the SAME client. Not carried into stage 5."""

from fastapi import APIRouter

from ..core.deps import HttpClientDep

router = APIRouter(prefix="/demo", tags=["lifespan demo"])


@router.get("/client-id")
def client_id(client: HttpClientDep):
    return {"client_id": id(client)}  # call it twice: the SAME number both times
