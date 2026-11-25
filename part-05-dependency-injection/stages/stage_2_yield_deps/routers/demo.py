"""
Stage 2 demo only — SEE the yield lifecycle. Not carried into stage 3.

A FakeSession prints OPEN / COMMIT / ROLLBACK / CLOSE, so the terminal shows
setup → route → teardown. No database needed yet (that's Part 06).
"""

from itertools import count
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ..services import rates as rate_service

router = APIRouter(prefix="/demo", tags=["yield demo"])
_ids = count(1)


class FakeSession:
    def __init__(self):
        self.id = next(_ids)
        print(f"  [session {self.id}] OPEN")

    def commit(self):
        print(f"  [session {self.id}] COMMIT")

    def rollback(self):
        print(f"  [session {self.id}] ROLLBACK")

    def close(self):
        print(f"  [session {self.id}] CLOSE")


def get_session():
    session = FakeSession()  # ── setup: open the resource
    try:
        yield session  # ── the route runs here
        session.commit()
    except Exception:
        session.rollback()  # something failed → undo
        raise  # always re-raise so FastAPI still returns the error
    finally:
        session.close()  # ── teardown: ALWAYS runs


SessionDep = Annotated[FakeSession, Depends(get_session)]


@router.get("/session/{code}")  # a normal request → OPEN, route, COMMIT, CLOSE
def with_session(code: str, session: SessionDep):
    print(f"  route running with session {session.id}")
    rate = rate_service.get_rate(code)
    if rate is None:
        raise HTTPException(status_code=404, detail="rate not found")
    return {"code": code.upper(), "inr_per_unit": rate, "session": session.id}


@router.get("/error")  # the route raises → OPEN, route, ROLLBACK, CLOSE
def error_route(session: SessionDep):
    print("  route about to fail…")
    raise HTTPException(status_code=500, detail="boom — watch the terminal: CLOSE still printed")


def get_audit_log(session: SessionDep):  # a yield dependency that depends on another one
    print("  [audit] START")
    yield f"audit-for-session-{session.id}"
    print("  [audit] END   (runs BEFORE the session closes)")


@router.get("/nested")  # teardown runs in REVERSE order of setup
def nested(audit: Annotated[str, Depends(get_audit_log)]):
    print("  route running")
    return {"audit": audit}
