"""
STAGE 4 (notes 07 → 09) — doing it PROPERLY by hand. This is why frameworks exist.

The stage 3 app, but now it behaves like a real API:
    - routing:      only GET /convert works; anything else is 404
    - methods:      POST /convert gets 405 Method Not Allowed
    - validation:   a missing or non-number amount gets 400 Bad Request, which we write ourselves
For ONE endpoint, it's already this long. Imagine 50 endpoints, plus docs, plus
JSON bodies, plus auth. And we still have no /docs page.

Stage 5 does ALL of this in about five lines.

Run:   uv run uvicorn stages.stage_4_asgi_pain:app --reload
Try:   http://127.0.0.1:8000/convert?amount=8300   → 200 {"usd": 100.0}
       http://127.0.0.1:8000/convert?amount=abc    → 400
       http://127.0.0.1:8000/nope                  → 404
       curl -X POST "http://127.0.0.1:8000/convert?amount=1"   → 405
"""

import json
from urllib.parse import parse_qs


def convert_inr_to_usd(amount):
    return {"usd": amount / 83.0}


async def send_json(send, status, data):
    body = json.dumps(data).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    # 1) routing — by hand
    if scope["path"] != "/convert":
        return await send_json(send, 404, {"detail": "Not Found"})

    # 2) method check — by hand
    if scope["method"] != "GET":
        return await send_json(send, 405, {"detail": "Method Not Allowed"})

    # 3) read + validate the query — by hand
    params = parse_qs(scope["query_string"].decode())
    if "amount" not in params:
        return await send_json(send, 400, {"detail": "amount is required"})
    try:
        amount = float(params["amount"][0])
    except ValueError:
        return await send_json(send, 400, {"detail": "amount must be a number"})

    # 4) the ONE real line
    result = convert_inr_to_usd(amount)

    # 5) respond — by hand
    await send_json(send, 200, result)
