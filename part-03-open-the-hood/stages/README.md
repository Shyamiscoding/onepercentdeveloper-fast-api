# Part 03 — the "open the hood" stages

Each file demonstrates ONE idea from the notes, so you can run it, see the idea,
then move on — no headache. Two kinds of files:

- **scripts** — just print output. Run with `python`.
- **apps** — run with `uvicorn` and try in `/docs`.

`../main.py` is the finished app with all the app-level pieces combined.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-03-open-the-hood
cp .env.example .env                            # needed by stages 6 & 8 and main.py
```

## The stages (in notes order)

| Stage | Notes | Run it | What it shows |
|-------|-------|--------|---------------|
| `stage_1_type_hint_passive`   | A1 | `uv run python stages/stage_1_type_hint_passive.py` | a type hint only describes |
| `stage_2_annotated`           | A2 | `uv run uvicorn stages.stage_2_annotated:app --reload` | Annotated attaches rules to the type |
| `stage_3_basemodel_pipeline`  | B1 | `uv run python stages/stage_3_basemodel_pipeline.py` | parse → validate → coerce → serialize |
| `stage_4_validators_computed` | B2 | `uv run uvicorn stages.stage_4_validators_computed:app --reload` | validators / computed / serializer |
| `stage_5_model_config`        | B3 | `uv run python stages/stage_5_model_config.py` | lax vs strict vs `extra="forbid"` |
| `stage_6_settings`            | B4 | `uv run uvicorn stages.stage_6_settings:app --reload` | settings from `.env` + the live 3rd-party API |
| `stage_7_json_schema`         | B5 | `uv run python stages/stage_7_json_schema.py` | model → JSON Schema → OpenAPI |
| `stage_8_async_vs_sync`       | C2 / C3 | `uv run uvicorn stages.stage_8_async_vs_sync:app --reload` | `async def` vs `def` + the blocking footgun |
| `../main.py`                  | all | `uv run uvicorn main:app --reload` | the finished app |

> B6 ("v1 → v2 / the Rust core") and C1 ("concurrency ≠ parallelism") are
> concept-only — nothing to run, so no stage.
