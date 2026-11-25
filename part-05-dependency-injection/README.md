# Part 05 — dependency injection

Part 04 gave the currency API a real layout (routers, services, schemas, core),
but every route still built what it needed itself. Part 05 wires it with
**dependency injection** — without changing what the API does — and adds the
pieces a real app needs: guards, a shared HTTP client, middleware & CORS, and
background work.

## How this folder is organised

```text
part-05-dependency-injection/
├─ stages/     the lesson, step by step — ONE new idea per stage
└─ src/        the finished app — all the stages combined into the final result
```

- **`stages/`** — the learning path. Each stage is a complete, runnable copy of
  the stage before it, plus exactly one new idea (Depends → yield dependencies →
  guards → lifespan → middleware & CORS → background tasks). Walk them in order
  to watch the app grow one step at a time. The full stage-by-stage guide, with a
  run command for each, lives in [`stages/README.md`](stages/README.md).
- **`src/`** — the destination. It's those six stages combined into one clean,
  finished app (stage 6 without its throwaway demo routes). This is what the
  Part 05 project looks like once every idea is in place.

> New here? Read through the stages first to learn each idea on its own, then open
> `src/` to see the whole thing assembled.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-05-dependency-injection
cp ../part-04-structure-and-di/.env .env   # reuse Part 04's .env — it has your real key
# or:  cp .env.example .env                # then paste your key into RATE_API_KEY
```

`RATE_API_KEY` is required (a missing key fails fast at startup). With the
placeholder key the app still starts; live routes answer **502 "rate provider
rejected RATE_API_KEY"**. Free key: https://openexchangerates.org
(the free plan allows ~1,000 calls a month, so don't hammer `/rates/live`).

## Run it

```bash
# the finished app
uv run uvicorn src.main:app --reload       # → http://127.0.0.1:8000/docs

# or any single stage (one at a time — they all use port 8000)
uv run uvicorn stages.stage_1_dependencies.main:app --reload
```

For every stage, what each one adds, and a guided tour through `/docs`, see
[`stages/README.md`](stages/README.md).
