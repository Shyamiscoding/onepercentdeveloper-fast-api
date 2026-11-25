# Part 01 — the bridge: your function, trapped, then set free

One story in five files. Each stage changes ONE thing, so walk them in order.

```text
stage 1  plain function        works, but trapped: runs once, only for you, then exits
   │     problem: it needs to be ALWAYS ON and to LISTEN + RESPOND → that's a server
   ▼
stage 2  uvicorn + ASGI peek   uvicorn is the server, but it only speaks ASGI:
   │                           async def app(scope, receive, send). Print what it hands you.
   ▼
stage 3  raw ASGI convert      your function online! but bytes, parsing, JSON, two sends,
   │                           all by hand. One real line, the rest is plumbing
   ▼
stage 4  raw ASGI, properly    add 404 / 405 / 400 by hand → it balloons. Hard to read,
   │                           hard to grow. This pain is WHY frameworks exist
   ▼
stage 5  FastAPI               the same function + 3 lines. Routing, validation, JSON
                               and /docs for free. Still uvicorn underneath
```

## Run them (from this folder, `part-01-the-bridge/`)

| Stage | Notes | Run it | Then open |
|-------|-------|--------|-----------|
| `stage_1_plain_function` | 01, 02 | `uv run python stages/stage_1_plain_function.py` | the terminal prints once, then exits |
| `stage_2_asgi_peek` | 07 | `uv run uvicorn stages.stage_2_asgi_peek:app --reload` | `/convert?amount=8300`, then watch the terminal |
| `stage_3_asgi_convert` | 07 | `uv run uvicorn stages.stage_3_asgi_convert:app --reload` | `/convert?amount=8300`, then `?amount=abc` (500) |
| `stage_4_asgi_pain` | 07 → 09 | `uv run uvicorn stages.stage_4_asgi_pain:app --reload` | `?amount=abc` (400), `/nope` (404) |
| `stage_5_fastapi` | 01, 09 | `uv run fastapi dev stages/stage_5_fastapi.py` | `/convert?amount=8300` and `/docs` |

All URLs are on http://127.0.0.1:8000. Stop a server with **Ctrl+C** before starting the next one.

## The one comparison worth making side by side

Open `stage_4_asgi_pain.py` and `stage_5_fastapi.py` side by side. Send the same
three requests to each (good amount, `abc`, `/nope`). Both answer 200 and 404 the same.
For `abc`, stage 4 sends the 400 we wrote by hand. FastAPI sends a 422 that names the
field and the reason, with zero code from us. One file is a page of plumbing; the other
is your function plus 3 lines.
