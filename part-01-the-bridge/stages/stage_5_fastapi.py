"""
STAGE 5 (notes 01 + 09) — the same thing with FastAPI. The magic reveal.

Your stage 1 function, plus three lines: the import, app = FastAPI(), and the
@app.get decorator. FastAPI IS an ASGI app, so uvicorn runs it exactly like
stage 3. FastAPI now does everything stage 4 did by hand:

    routing          /nope                  → 404
    methods          POST /convert          → 405
    validation       ?amount=abc            → 422, naming the field and the reason (stage 4 wrote its own 400)
    types            "8300" in the URL      → 8300.0, a real float (thanks to `amount: float`)
    JSON             your dict              → a JSON response
    docs             /docs                  → free interactive docs (stage 4 had none)

Run it either way. It's the SAME uvicorn underneath:
    uv run fastapi dev stages/stage_5_fastapi.py
    uv run uvicorn stages.stage_5_fastapi:app --reload

Open:  http://127.0.0.1:8000/convert?amount=8300
       http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/convert")
def convert_inr_to_usd(amount: float):
    return {"usd": amount / 83.0}
