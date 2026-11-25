# Part 03 — open the hood

Part 03 looks under FastAPI's hood: type hints vs `Annotated`, Pydantic v2 (the
parse → validate → coerce → serialize pipeline, validators, model config, JSON
Schema), settings from `.env`, and `async def` vs `def`. It ends with a currency
API that reads settings and calls a real exchange-rate provider.

## How this folder is organised

```text
part-03-open-the-hood/
├─ stages/       the lesson, step by step — ONE idea per file (stage_1 … stage_8)
├─ main.py       the finished app — the app-level pieces combined (the final result)
├─ config.py     Settings read from .env
└─ .env.example  copy to .env:  cp .env.example .env
```

- **`stages/`** — the learning path. Two kinds of file: **scripts** (just print —
  run with `python`) and **apps** (run with `uvicorn`, try in `/docs`). The full
  stage-by-stage table is in [`stages/README.md`](stages/README.md).
- **`main.py`** — the destination: the finished app with every app-level piece
  combined.

> New here? Walk the stages in order, then run `main.py` to see the finished API.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-03-open-the-hood
cp .env.example .env    # needed by stages 6 & 8 and main.py — paste your key into RATE_API_KEY
```

`RATE_API_KEY` is a free key from https://openexchangerates.org (the free plan
allows ~1,000 calls a month, so don't hammer `/rates/live`). A Postman collection,
`OnePercent-Part03.postman_collection.json`, is included if you prefer it to `/docs`.

## Run it (from this folder)

```bash
uv run python stages/stage_1_type_hint_passive.py     # a script stage
uv run uvicorn stages.stage_6_settings:app --reload   # an app stage → /docs
uv run uvicorn main:app --reload                      # the finished app
```

Use one server at a time (they all use port 8000) — press **Ctrl+C** before
starting the next.
