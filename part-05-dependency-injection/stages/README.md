# Part 05 — dependency injection: the stages

## The story: Part 04's layout, wired with dependencies

Part 04 cut Part 03's one big file into a real layout: routers, services, schemas,
core. But every route still builds what it needs itself: its own `Settings()`, its
own HTTP client for the live rate API. Part 05 fixes that **without changing what
the API does**.

Every stage is a copy of the stage before it, plus ONE new idea. Stage 1 starts
from Part 04's `stage_1_layout/`:

```text
../part-04-structure-and-di/stages/stage_1_layout/   Part 04's layout
  └► stage_1_dependencies/   + core/deps.py: routes ASK for things (Depends)
       └► stage_2_yield_deps/   + a yield dependency: one HTTP client per request
            └► stage_3_scoped_deps/   + guards on a route, a router (admin.py), the whole app
                 └► stage_4_lifespan/   + lifespan: ONE HTTP client for the whole process
                      └► stage_5_cors_middleware/   + timing middleware and CORS
                           └► stage_6_background_tasks/   + work that runs after the reply
                                └► ../src/   the finished app = stage 6 without its demo
```

Want to see exactly what an idea added? Diff two neighbouring stages:

```bash
diff -r ../part-04-structure-and-di/stages/stage_1_layout stages/stage_1_dependencies
diff -r stages/stage_1_dependencies stages/stage_2_yield_deps
```

Each stage's `main.py` docstring lists what changed. A stage may also have a
`routers/demo.py` (and stage 1 a `routers/before_di.py`): those are experiments for
THAT stage only, so they are not copied into the next one. Everything else carries forward.

It still forgets everything on restart. That's on purpose: it's Part 06's problem.

## The one question of this part: where should a thing live?

Follow the HTTP client for the live rate through the stages. Only `core/deps.py`
changes; the routes never notice:

| Lives… | Stage | How | Right for |
|--------|-------|-----|-----------|
| per **call** | Part 04, 1 | `async with httpx.AsyncClient()` inside the function | quick demos only |
| per **request** | 2, 3 | a `yield` dependency opens it, closes it after the response | DB sessions (Part 06) |
| per **process** | 4 → | `lifespan` opens ONE at startup, every request shares it | HTTP clients, pools, settings |
| **forever** | Part 06 | the database | rates, conversions |

And the rule that decides how a function gets what it needs:

> **If FastAPI calls it (a route, or a dependency), it can ask with `Depends`.
> If YOU call it (a service, a helper), give it plain parameters.**
> Stage 1's `/demo/wrong-call` shows what happens when you break this.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-05-dependency-injection
cp ../part-04-structure-and-di/.env .env   # easiest: reuse Part 04's .env, it has your real key
# or:  cp .env.example .env                # then paste your key into RATE_API_KEY
```

`RATE_API_KEY` is required, exactly like Parts 03–04 (a missing key fails fast at
startup). With the placeholder key the app still starts; live routes answer
**502 "rate provider rejected RATE_API_KEY"**. Free key: https://openexchangerates.org
(the free plan allows ~1,000 calls a month, so don't hammer `/rates/live`).

## The stages (in notes order)

Run every stage from `part-05-dependency-injection/`, one at a time (they all use port 8000).

| Stage | Notes | Run it | What it adds |
|-------|-------|--------|--------------|
| `stage_1_dependencies/` | A1 | `uv run uvicorn stages.stage_1_dependencies.main:app --reload` | `core/deps.py`: pagination, a class filter, the settings → provider tree; `/before/*` to compare; caching and **the rule** in `/demo/*` |
| `stage_2_yield_deps/` | A2 | `uv run uvicorn stages.stage_2_yield_deps.main:app --reload` | `get_http_client` as a `yield` dependency (one client per request); `/demo/*` prints a session's whole lifecycle |
| `stage_3_scoped_deps/` | A3 | `uv run uvicorn stages.stage_3_scoped_deps.main:app --reload` | `log_request` on the app, `require_api_key` on `routers/admin.py` and on `POST /rates/sync` |
| `stage_4_lifespan/` | A4 | `uv run uvicorn stages.stage_4_lifespan.main:app --reload` | ONE shared client, live rates loaded once at startup (with a fallback), `/uptime` |
| `stage_5_cors_middleware/` | A5 | `uv run uvicorn stages.stage_5_cors_middleware.main:app --reload` + `cors_test.html` | a timing middleware + CORS working / blocked in a real browser |
| `stage_6_background_tasks/` | A6 | `uv run uvicorn stages.stage_6_background_tasks.main:app --reload` | `POST /convert` logs after the reply; `POST /rates/sync` answers 202 and syncs after |
| **`../src/`** | all | `uv run uvicorn src.main:app --reload` | **the finished app** — stage 6 without its demo |

## The finished app (`../src/`)

```text
src/
├─ main.py                    the assembler: lifespan (ONE http client), middleware, CORS, routers
├─ core/config.py             Part 03's Settings, via get_settings() + admin_api_key
├─ core/deps.py               SettingsDep, PageParams, FilterDep, HttpClientDep, ProviderDep,
│                             require_api_key, log_request
├─ schemas/rates.py           Part 03's shapes (Currency, RateIn, ConversionResult) + RatePage
├─ services/rate_provider.py  Part 03's live call + RateProvider
├─ services/rates.py          the business logic — rates still in a dict, no FastAPI imports
└─ routers/                   rates.py · admin.py · convert.py · health.py — thin
```

A demo path through it in `/docs`: `GET /uptime` (`"rates_source": "live"`) →
`GET /rates` → `POST /rates/sync` without a key (**401**) → with `x-api-key: secret`
(**202**, and the 🔄 line prints) → `POST /admin/rates` with the key to add
`{"code": "SGD", "inr_per_unit": 64}` → `GET /rates/SGD` → `POST /convert` (the 📝
audit log prints 2 s later). Then **restart the server** and `GET /rates/SGD`:
**404**, the rate you added is gone. That's the cliffhanger for Part 06.
