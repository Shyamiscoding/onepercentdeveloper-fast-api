# Part 04 — project structure: the stage

## The story: Part 03's currency API, given a shape

Part 03 ended with one `main.py`: the `/rates` CRUD, `/convert`, and `/rates/live`
calling a real exchange-rate API. It works, but it's one big file. Part 04 cuts it
into a real project layout **without changing what the API does**.

```text
stage_1_layout/      Part 03, cut into core/ routers/ schemas/ services/
  └► ../src/         the finished app = the same layout
```

Every route still builds what it needs itself (its own settings, its own HTTP
client). That's Part 05's problem: dependency injection. Part 05 starts from this
exact folder and adds one idea per stage.

## The one rule of this layout: thin routes, fat services

| Folder | One job |
|--------|---------|
| `routers/` | **thin**: read the request, call a service, return (status codes, 404s) |
| `services/` | **fat**: the real work (the maths, the live rate call), no FastAPI imports |
| `schemas/` | Pydantic shapes: what comes in, what goes out |
| `core/` | things the whole app shares: `config.py` (Part 03's Settings) |
| `main.py` | the assembler: create the app, `include_router`, nothing else |

Routers import services, never the other way round.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-04-structure-and-di
cp ../part-03-open-the-hood/.env .env      # easiest: reuse Part 03's .env, it has your real key
# or:  cp .env.example .env                # then paste your key into RATE_API_KEY
```

`RATE_API_KEY` is required, exactly like Part 03 (a missing key fails fast at
startup). With the placeholder key the app still starts; live routes answer
**502 "rate provider rejected RATE_API_KEY"**. Free key: https://openexchangerates.org
(the free plan allows ~1,000 calls a month, so don't hammer `/rates/live`).

## Run it

| Stage | Notes | Run it | What it shows |
|-------|-------|--------|---------------|
| `stage_1_layout/` | A1 | `uv run uvicorn stages.stage_1_layout.main:app --reload` | Part 03 cut into routers / schemas / services / core, behaviour unchanged |
| **`../src/`** | all | `uv run uvicorn src.main:app --reload` | **the finished app** — the same layout |

Open `/docs`: the same endpoints as Part 03. We only reorganised the inside.

## The finished app (`../src/`)

```text
src/
├─ main.py                    the assembler: create the app, include the routers
├─ core/config.py             Part 03's Settings, moved
├─ schemas/rates.py           Part 03's shapes (Currency, RateIn, ConversionResult)
├─ services/rate_provider.py  Part 03's live call, moved out of the route
├─ services/rates.py          the business logic — rates in a dict, no FastAPI imports
└─ routers/                   rates.py · convert.py — thin
```
