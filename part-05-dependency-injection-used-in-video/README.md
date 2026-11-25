# Part 05 — the exact copy used in the video

This folder is the **live-coding copy as it appeared on screen** during the
Part 05 video. It's kept here on purpose so you can follow along line by line and
see exactly what was typed while recording.

> For the clean, final, stage-by-stage version of Part 05, use
> [`../part-05-dependency-injection/`](../part-05-dependency-injection/). This
> folder is the "as recorded" copy, not the polished one — a few names differ
> (see [What differs from the polished version](#what-differs-from-the-polished-version) below).

## What's in here

```text
part-05-dependency-injection-used-in-video/
├─ src/              the app as built on camera (one finished package)
│  ├─ main.py           lifespan + a global log dependency + timing middleware + CORS
│  ├─ core/             config.py (Settings) · deps.py (log_request, the HTTP client)
│  ├─ routers/          rates.py · convert.py · health.py — thin
│  ├─ schemas/          Pydantic shapes
│  └─ services/         rates.py · rate_provider.py — the real work
└─ cors-demo.html    the browser page used in the CORS part of the video
```

The app is the same currency converter, wired with the Part 05 ideas:

- a **lifespan** that opens ONE shared `httpx` client for the whole process and
  records start time (powers `GET /uptime`),
- a global **`log_request`** dependency on every route,
- a **timing middleware** that adds a custom response header, and
- **CORS**, so a browser page on another origin can call the API.

## Setup (packages are already installed by `uv sync` in `fastapi-code/`)

```bash
cd part-05-dependency-injection-used-in-video
cp ../part-04-structure-and-di/.env .env   # reuse an earlier .env — it has your real key
# or:  cp .env.example .env                # then paste your key into RATE_API_KEY
```

`RATE_API_KEY` is a free key from https://openexchangerates.org (the free plan
allows ~1,000 calls a month, so don't hammer `/rates/live`).

## Run the API

```bash
uv run uvicorn src.main:app --reload       # → http://127.0.0.1:8000/docs
```

Try `GET /uptime`, `GET /rates`, and `POST /convert` in `/docs`.

## Run the CORS demo

CORS only lets the page read the response when it's served from the **allowed
origin** (`http://localhost:3001`). With the API running, in a second terminal:

```bash
cd part-05-dependency-injection-used-in-video
python -m http.server 3001                 # serve this folder on the allowed origin
```

Open `http://localhost:3001/cors-demo.html` and click **Call the API** → the
browser lets JavaScript read the rates (**allowed**). Serve the page from any other
port (e.g. `python -m http.server 3002`) and the same call is **blocked** — the
request still reaches the server, but the browser withholds the body. Open DevTools
Console to read the exact CORS message.

## What differs from the polished version

Because this is the on-screen copy, not the cleaned-up one:

- the custom timing header is named `shyam-process-time-ms` (the polished version
  uses `X-Process-Time-ms`),
- CORS allows `http://localhost:3001`.

Everything behaves the same — these are just the names as they were typed in the
video. For the tidy, organised version, see
[`../part-05-dependency-injection/`](../part-05-dependency-injection/).
