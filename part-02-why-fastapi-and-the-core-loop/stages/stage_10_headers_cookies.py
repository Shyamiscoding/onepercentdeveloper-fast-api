"""
STAGE 10 (notes B10) — headers & cookies.

Not every input rides in the path, query, or body. Request METADATA travels in
headers (User-Agent, Authorization, custom X-* keys) and in cookies (a session
id). Same clean, typed treatment as everything else: one Header() / Cookie()
param and FastAPI pulls the value off the request and hands it to you.

Header-name gotcha: HTTP headers use hyphens and are case-insensitive, but
Python identifiers can't contain hyphens. So FastAPI maps the argument name to
a header by turning underscores into hyphens:
    user_agent  -> "User-Agent"
    x_api_key   -> "X-API-Key"
(Pass Header(convert_underscores=False) if you must match a raw underscore.)

Try with curl:
    curl http://127.0.0.1:8000/whoami \
         -H "User-Agent: demo-client/1.0" \
         --cookie "session=abc123"

    curl http://127.0.0.1:8000/protected -H "X-API-Key: secret123"   # 200
    curl http://127.0.0.1:8000/protected                             # 401

Run:  uv run uvicorn stages.stage_10_headers_cookies:app --reload
"""

from fastapi import Cookie, FastAPI, Header, HTTPException

app = FastAPI(title="Rates API — Stage 10 (headers & cookies)")


# NEW in this stage: read request metadata with Header() and Cookie()
@app.get("/whoami")
def whoami(
    user_agent: str | None = Header(default=None),  # maps to the "User-Agent" header
    session: str | None = Cookie(default=None),  # reads the "session" cookie
):
    return {"user_agent": user_agent, "session": session}


# a CUSTOM header carrying a credential — x_api_key maps to "X-API-Key".
# headers are a common home for auth, so this reuses the B8 error pattern.
@app.get("/protected")
def protected(x_api_key: str | None = Header(default=None)):
    if x_api_key != "secret123":
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")
    return {"ok": True, "you_sent": x_api_key}
