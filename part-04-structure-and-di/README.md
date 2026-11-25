# Part 04 — project structure

Part 03 ended with everything in one `main.py`: the `/rates` CRUD, `/convert`,
and `/rates/live` calling a real exchange-rate API. It works, but it's one big
file. Part 04 cuts it into a **real project layout** — routers, services,
schemas, core — **without changing what the API does**. `/docs` looks exactly
like Part 03; only the inside is reorganised.

## How this folder is organised

```text
part-04-structure-and-di/
├─ stages/     the lesson, step by step
│  └─ stage_1_layout/   Part 03's one file, cut into core/ routers/ schemas/ services/
└─ src/        the finished app — the same layout, cleaned up (the final result)
```

- **`stages/`** — the learning path. Part 04 has a single stage,
  `stage_1_layout/`: it takes Part 03's one big file and splits it into a real
  package, with behaviour unchanged. The full walkthrough and the run command live
  in [`stages/README.md`](stages/README.md).
- **`src/`** — the destination: the finished app in the same layout. This is the
  starting point Part 05 builds on.

The layout follows one rule — **thin routes, fat services**: `routers/` read the
request and call a service; `services/` do the real work with no FastAPI imports;
`schemas/` hold the Pydantic shapes; `core/` holds what the whole app shares; and
`main.py` just assembles everything. Routers import services, never the other way
round.

> New here? Read `stages/stage_1_layout/` to see the split, then open `src/` for
> the finished version.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-04-structure-and-di
cp ../part-03-open-the-hood/.env .env   # reuse Part 03's .env — it has your real key
# or:  cp .env.example .env             # then paste your key into RATE_API_KEY
```

`RATE_API_KEY` is required (a missing key fails fast at startup). With the
placeholder key the app still starts; live routes answer **502 "rate provider
rejected RATE_API_KEY"**. Free key: https://openexchangerates.org
(the free plan allows ~1,000 calls a month, so don't hammer `/rates/live`).

## Run it

```bash
# the finished app
uv run uvicorn src.main:app --reload                   # → http://127.0.0.1:8000/docs

# or the stage
uv run uvicorn stages.stage_1_layout.main:app --reload
```

See [`stages/README.md`](stages/README.md) for the full walkthrough.
