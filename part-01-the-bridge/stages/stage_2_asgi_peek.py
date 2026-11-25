"""
STAGE 2 (notes 07) — bring in a server: uvicorn. But it only talks ASGI.

uvicorn solves "always on" and "listen": it keeps running, owns port 8000 and
accepts every request. But it won't call ANY function. Your code has to
match the shape uvicorn expects. That shape is called ASGI:

    async def app(scope, receive, send): ...

    scope    a dict describing the request (method, path, query, headers)
    receive  await it to read the request body
    send     await it to send the response back, in pieces

This stage does nothing useful on purpose. It PRINTS what uvicorn hands
you, so you can see the raw request before any framework tidies it up.

Run:   uv run uvicorn stages.stage_2_asgi_peek:app --reload
Open:  http://127.0.0.1:8000/convert?amount=8300
Watch the TERMINAL: path is a str, but query_string and headers are raw BYTES.
"""

from pprint import pprint


async def app(scope, receive, send):
    if scope["type"] != "http":  # uvicorn also sends "lifespan" (startup/shutdown) events
        return

    print("\n------ what uvicorn handed us ------")
    pprint({k: scope[k] for k in ("method", "path", "query_string", "headers")})

    await send(
        {  # a response is TWO messages: start (status + headers) ...
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send(
        {"type": "http.response.body", "body": b"look at your terminal"}
    )  # ... then the body
