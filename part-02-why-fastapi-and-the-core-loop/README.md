# Part 02 — why FastAPI, and the core loop

Part 02 builds the `/rates` CRUD, then hardens it one layer at a time: the path,
the query, the body, each field, the output shape, status codes, errors, forms &
files, and headers & cookies. Ten small steps that turn a raw CRUD into a properly
validated API.

## How this folder is organised

```text
part-02-why-fastapi-and-the-core-loop/
├─ stages/          the lesson, step by step — ONE idea per file (stage_1 … stage_10)
├─ main.py          the finished app — all ten stages combined (the final result)
└─ sample-uploads/  CSV files used by stage_9 (forms & files)
```

- **`stages/`** — the learning path. Each file is a complete, runnable app at one
  point in the story: open it, run it, see the new idea, move to the next. The full
  stage-by-stage table is in [`stages/README.md`](stages/README.md).
- **`main.py`** — the destination: the fully hardened app with every stage combined.

> New here? Walk the stages in order, then run `main.py` to see the finished API.

## Run it (from this folder)

```bash
cd part-02-why-fastapi-and-the-core-loop
uv run uvicorn stages.stage_1_crud_raw:app --reload   # any single stage
uv run uvicorn main:app --reload                      # the finished app
```

then open http://127.0.0.1:8000/docs. No `.env` or API key is needed for Part 02.
Use one server at a time (they all use port 8000) — press **Ctrl+C** before
starting the next.
