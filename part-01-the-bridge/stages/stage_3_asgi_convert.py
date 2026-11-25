"""
STAGE 3 (notes 07) — your function, ONLINE, the hard way (raw ASGI).

The stage 1 function, wrapped so uvicorn can call it. It works: your function
is now always on and answers over HTTP. But count the lines that are NOT
your function. You decode bytes, parse the query, convert types, encode JSON
and send two messages by hand. Only ONE line is the actual conversion.

Run:   uv run uvicorn stages.stage_3_asgi_convert:app --reload
Open:  http://127.0.0.1:8000/convert?amount=8300      → {"usd": 100.0}

Now try to break it (stage 4 shows what fixing these costs):
    http://127.0.0.1:8000/convert?amount=abc    → crash, 500 Internal Server Error
    http://127.0.0.1:8000/convert               → crash, 500 (no amount at all)
    http://127.0.0.1:8000/hello?amount=8300     → still converts! there's no routing

(A traceback may show up in the terminal even on the happy path. That's your
browser quietly asking for /favicon.ico, which has no ?amount, so it crashes too.)
"""

import json
from urllib.parse import parse_qs


def convert_inr_to_usd(amount):
    return {"usd": amount / 83.0}


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    # read ?amount=... from the URL — it arrives as raw bytes
    params = parse_qs(scope["query_string"].decode())
    amount = float(params["amount"][0])

    # the ONE real line — convert
    result = convert_inr_to_usd(amount)

    # reply by hand: status + headers first, then the body (as bytes)
    body = json.dumps(result).encode()
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": body})
