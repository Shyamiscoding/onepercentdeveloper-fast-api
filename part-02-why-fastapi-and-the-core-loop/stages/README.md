# Part 02 — the CRUD-then-harden stages

Each file is a **complete, runnable app** at one point in the story. Open the
file for the idea you're learning, run it, see the new idea working, then move
to the next. `../main.py` is the finished app (all stages combined).

Run any stage from **this part's folder** (`part-02-why-fastapi-and-the-core-loop/`):

```bash
uv run uvicorn stages.stage_1_crud_raw:app --reload
uv run uvicorn main:app --reload          # the finished app
```

then open http://127.0.0.1:8000/docs

Notes A1–A4 (who made FastAPI and why it took off) are story, not code. For B0,
open `../../uv.lock` after `uv sync` and find `starlette` and `pydantic` pinned
as FastAPI's two halves.

| Stage | Notes | What it adds |
|-------|-------|--------------|
| `stage_1_crud_raw`      | B1 | the whole `/rates` CRUD — **no validation** |
| `stage_2_path_enum`     | B2 | harden the **path** with an `Enum` |
| `stage_3_query`         | B3 | harden the **query** with `Query()` |
| `stage_4_body`          | B4 | real writes take a **body** (`BaseModel`) |
| `stage_5_fields`        | B5 | harden each **field** with `Field()` |
| `stage_6_response_model`| B6 | shape the **output** with `response_model` |
| `stage_7_status`        | B7 | honest **status codes** (201 / 204) |
| `stage_8_errors`        | B8 | **errors** — the 404 stage 1 was missing |
| `stage_9_forms_files`   | B9 | **forms & files** (uses `../sample-uploads/`) |
| `stage_10_headers_cookies` | B10 | read **headers & cookies** with `Header()` / `Cookie()` |
| `../main.py`            | B1–B10 | the finished, fully-hardened app |
