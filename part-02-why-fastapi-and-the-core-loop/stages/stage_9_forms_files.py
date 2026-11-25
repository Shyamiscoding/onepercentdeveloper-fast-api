"""
STAGE 9 (notes B9) — forms & files.

Not everything is JSON. HTML form data and file uploads get the same clean,
typed treatment. One `file: UploadFile` param and you can accept uploads.

Demo files live in  ../sample-uploads/  (amounts-small.csv, amounts-medium.csv,
transactions.csv). In Postman: POST /convert/csv -> Body -> form-data ->
key "file", switch its type to File, pick a CSV, Send. (rows includes the
header line, since we just count raw lines.)

async / await here: reading the uploaded file is I/O. async lets this request
step aside while it waits, so the worker can serve others. We open async up
properly in Part 03.

Run:  uv run uvicorn stages.stage_9_forms_files:app --reload
"""

from fastapi import FastAPI, UploadFile

app = FastAPI(title="Rates API — Stage 9 (forms & files)")


# one file
@app.post("/convert/csv")
async def convert_csv(file: UploadFile):
    content = await file.read()
    lines = content.decode().splitlines()
    return {"filename": file.filename, "rows": len(lines)}


# many files — same idea, typed as a list (send the "files" key several times)
@app.post("/convert/csv-many")
async def convert_many(files: list[UploadFile]):
    out = []
    for f in files:
        content = await f.read()
        out.append({"filename": f.filename, "rows": len(content.decode().splitlines())})
    return {"count": len(files), "files": out}
