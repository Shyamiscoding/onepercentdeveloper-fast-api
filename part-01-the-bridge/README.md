# Part 01 — the bridge

How does a plain Python function become a web API? Part 01 walks that bridge in
five small files: a function that runs once, then a real server (uvicorn) speaking
raw ASGI by hand, then the same function on FastAPI in three lines — with routing,
validation, and `/docs` for free.

## How this folder is organised

```text
part-01-the-bridge/
└─ stages/     the lesson, step by step — five files, each changes ONE thing
```

Part 01 has no `src/` or separate finished app: the **last stage,
`stage_5_fastapi.py`, is the destination.** Walk the five files in order to feel
why frameworks exist.

- `stage_1_plain_function.py` — a plain function (a **script**: run with `python`)
- `stage_2_asgi_peek.py` … `stage_4_asgi_pain.py` — uvicorn + raw ASGI by hand (**apps**)
- `stage_5_fastapi.py` — the same function + 3 lines of FastAPI (**app**)

Scripts print to the terminal; apps run under a server and open in the browser.
The full stage-by-stage guide, with a run command for each, is in
[`stages/README.md`](stages/README.md).

## Run it (from this folder)

```bash
cd part-01-the-bridge
uv run python stages/stage_1_plain_function.py            # a script stage
uv run uvicorn stages.stage_3_asgi_convert:app --reload   # an app stage → http://127.0.0.1:8000
uv run fastapi dev stages/stage_5_fastapi.py              # the FastAPI finale → /docs
```

No `.env` or API key is needed for Part 01. Use one server at a time (they all use
port 8000) — press **Ctrl+C** before starting the next.
