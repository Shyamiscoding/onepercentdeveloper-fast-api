<p align="center">
  <a href="https://www.onepercentdeveloper.com/">
    <img src="assets/onepercentdeveloper-logo.svg" width="96" height="96" alt="One Percent Developer — onepercentdeveloper.com" />
  </a>
</p>

<h1 align="center">OnePercent — FastAPI in Kannada: the code</h1>

<p align="center">
  <a href="https://www.onepercentdeveloper.com/"><b>One Percent Developer</b></a> ·
  <a href="https://www.onepercentdeveloper.com/">onepercentdeveloper.com</a>
</p>

Runnable code for the **FastAPI [ ಕನ್ನಡದಲ್ಲಿ ] — Zero to 1% Developer** course,
part by part, in the order it's taught. Each part folder matches one video.

**Website:** [onepercentdeveloper.com](https://www.onepercentdeveloper.com/)  
**Full playlist:** [FastAPI — Zero to 1% Developer](https://www.youtube.com/playlist?list=PLDpu1sm2maWQ)  
**Channel:** [@shyamiscoding](https://www.youtube.com/channel/UCT0629rHJIjJWmQj1JyejyA)

> More free courses and the full Zero-to-1%-Developer journey are at
> **[onepercentdeveloper.com](https://www.onepercentdeveloper.com/)** — come join in.

## Watch the course

Click any thumbnail to watch the video; the code for that episode is in the folder
next to it.

| Video                                                                                | Part & code folder                                                                                                                                                                                                                 |
| :----------------------------------------------------------------------------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![FastAPI in Kannada — Part 1](https://img.youtube.com/vi/kU6GxIBNlAE/mqdefault.jpg) | **Part 01 — the bridge** A plain function → raw ASGI on uvicorn → FastAPI in 3 lines. (5 stages) Folder: [`part-01-the-bridge/`](part-01-the-bridge/)                                                                              |
| ![FastAPI in Kannada — Part 2](https://img.youtube.com/vi/_tDTmhkQ9vg/mqdefault.jpg) | **Part 02 — why FastAPI & the core loop** The `/rates` CRUD, then harden path, query, body, output, and errors. (10 stages + `main.py`) Folder: [`part-02-why-fastapi-and-the-core-loop/`](part-02-why-fastapi-and-the-core-loop/) |
| ![FastAPI in Kannada — Part 3](https://img.youtube.com/vi/bL1goe5BdpQ/mqdefault.jpg) | **Part 03 — open the hood** Type hints, Pydantic v2, settings from `.env`, and async vs sync. (8 stages + `main.py`) Folder: [`part-03-open-the-hood/`](part-03-open-the-hood/)                                                    |
| ![FastAPI in Kannada — Part 4](https://img.youtube.com/vi/8e6OD2xTYZ4/mqdefault.jpg) | **Part 04 — project structure** One file → a real layout: APIRouter, thin routes, fat services. (1 stage + `src/`) Folder: [`part-04-structure-and-di/`](part-04-structure-and-di/)                                                |
| ![FastAPI in Kannada — Part 5](https://img.youtube.com/vi/7EJHfoNVcjE/mqdefault.jpg) | **Part 05 — dependency injection** Depends, yield dependencies, guards, lifespan, middleware & CORS, background tasks. (6 stages + `src/`) Folder: [`part-05-dependency-injection/`](part-05-dependency-injection/)                |

> New parts are added here as each video goes live. When one appears, run `uv sync`
> again (see below) to pick up any new packages.

## Requirements

- **Python 3.13+** — declared in `pyproject.toml` (`requires-python = ">=3.13"`).
- **[uv](https://docs.astral.sh/uv/)** — the only tool you need. It installs the
right Python, creates the virtual environment, and installs every package.

Install `uv` first (one time):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# or with Homebrew:  brew install uv
# Windows (PowerShell):  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

There is **no `requirements.txt`** and no manual `pip install`: dependencies are
declared in `pyproject.toml` and pinned exactly in `uv.lock`, so everyone gets the
same versions.

## Set up once

```bash
git clone https://github.com/<your-username>/<this-repo>.git
cd fastapi-code
uv sync            # creates .venv and installs everything the parts need
```

There is **one** project (`pyproject.toml`) for the whole course, so you never run
`uv init` or `uv add` inside a part. When a new part is added, just run `uv sync`
again.

## Run the code

Every part has two kinds of file:

- **Scripts** — just print to the terminal. Run with `python`.
- **Apps** — have `app = FastAPI(...)`. Run with `uvicorn` and open the browser or
`/docs`.

```bash
cd part-01-the-bridge                                       # 1) go into the part
uv run python stages/stage_1_plain_function.py             # 2a) a SCRIPT stage
uv run uvicorn stages.stage_3_asgi_convert:app --reload    # 2b) an APP stage → http://127.0.0.1:8000
```

How to tell them apart: if the file has `app = ...`, it's an app — run it with
uvicorn and open `/docs`. Otherwise it's a script — run it with python and read the
terminal. **Every file's docstring at the top says exactly how to run it and what
to try.** All app stages use port 8000, so run one server at a time (press
**Ctrl+C** before the next, or add `--port 8001`).

## Environment & the API key

From Part 03 on, the app calls a live exchange-rate API, so it reads a key from a
`.env` file that lives **inside each part folder** (next to that part's code), not
in the repo root.

```bash
cd part-03-open-the-hood
cp .env.example .env     # then open .env and paste your key into RATE_API_KEY
```

- Get a free key ("App ID") from <https://openexchangerates.org> (the free plan
allows ~1,000 calls a month, so don't hammer `/rates/live`).
- Carry it forward into the next part: `cp ../part-03-open-the-hood/.env .env`.
- `.env` is **gitignored and never committed** — only `.env.example` (no real
secrets) is. Parts 01–02 need no key.

## Folder structure

```text
fastapi-code/
├─ README.md             ← you are here
├─ pyproject.toml        ← one project, all dependencies
├─ uv.lock              ← exact, pinned versions (don't edit by hand)
├─ .gitignore
├─ part-01-the-bridge/
├─ part-02-why-fastapi-and-the-core-loop/
├─ part-03-open-the-hood/
├─ part-04-structure-and-di/
├─ part-05-dependency-injection/
└─ part-05-dependency-injection-used-in-video/   ← the exact copy shown in the Part 5 video
```

Each part has its own `README.md` and follows the same shape:

```text
part-0N-<name>/
├─ README.md              ← start here for that part
├─ stages/
│  ├─ README.md           ← the stage-by-stage table + run commands
│  ├─ stage_1_<idea>.py   ← one idea per file, in teaching order
│  └─ ...
├─ main.py                ← (Parts 02, 03) the finished app, all stages combined
├─ src/                   ← (Parts 04–05) the finished app as a real package
├─ config.py              ← (Part 03) Settings read from .env
└─ .env.example           ← copy to .env:  cp .env.example .env
```

## Good to know

- **Run from inside the part folder.** Stages read that part's `.env` and import
its config, so the part folder must be the current directory. From Part 04 on,
each stage is a whole package; from Part 05 on, each stage is the previous one
plus exactly one new idea.
- **One app, all the way.** From Part 03 on, every part keeps growing the same
currency converter and the same live rate provider (openexchangerates.org).
- **One server at a time.** All app stages use port 8000 — press **Ctrl+C** before
starting the next, or add `--port 8001`.
- **Secrets stay out of git.** `.env`, `.venv/`, and `__pycache__/` are gitignored;
only `.env.example` is committed.
