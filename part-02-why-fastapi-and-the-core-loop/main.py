"""
OnePercent FastAPI course — Part 02, the FINISHED app (B1 - B10, fully hardened).

The /rates CRUD resource + the /convert endpoint, hardened piece by piece:
  path (Enum) · query (Query) · body (BaseModel) · fields (Field) ·
  response_model · status codes · errors (HTTPException) · forms/files · headers.

This is the "after" picture. To teach it live, walk the numbered files in
./stages/ (stage 1 = raw CRUD, then one new idea per file) and land here.

Run:  uv run uvicorn main:app --reload      then open  http://127.0.0.1:8000/docs
"""

from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import Cookie, FastAPI, Header, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="OnePercent Rates API", version="1.0.0")

# ---- in-memory store: resets every restart (fine for now; a real app uses a DB) ----
RATES_TO_INR: dict[str, float] = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


# ---- B2: a value from a FIXED set -> Enum (auto 422 + a dropdown in /docs) ----
class Currency(StrEnum):
    usd = "USD"
    eur = "EUR"
    gbp = "GBP"


# ---- B4 + B5: request body shapes, with per-field rules via Field() ----
class RateIn(BaseModel):
    code: str = Field(
        min_length=3, max_length=3, pattern="^[A-Z]{3}$", description="ISO currency code, e.g. USD"
    )
    inr_per_unit: float = Field(gt=0, le=100_000, description="Rate in INR")


class ConversionRequest(BaseModel):
    amount: float
    to: Currency = Currency.usd


# ---- B6: OUTPUT shapes. response_model filters what leaves = a security boundary ----
class ConversionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    amount_inr: Decimal
    to: Currency
    converted: Decimal


class SubscriberIn(BaseModel):
    email: EmailStr
    password: str  # comes IN with the request


class SubscriberPublic(BaseModel):
    id: UUID
    email: EmailStr  # notice: NO password here -> can never leak


# ============================  /rates  — the full CRUD  ============================
@app.get("/rates")  # READ all
def list_rates(limit: int = Query(default=10, ge=1, le=100, description="How many to return")):
    return dict(list(RATES_TO_INR.items())[:limit])


@app.get("/rates/{code}")  # READ one — B8: 404 instead of a crash
def get_rate(code: str):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    return {"code": code, "inr_per_unit": RATES_TO_INR[code]}


@app.post("/rates", status_code=status.HTTP_201_CREATED)  # CREATE — B7: 201
def create_rate(rate: RateIn):
    RATES_TO_INR[rate.code] = rate.inr_per_unit
    return rate


@app.put("/rates/{code}")  # UPDATE
def update_rate(code: str, rate: RateIn):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    RATES_TO_INR[code] = rate.inr_per_unit
    return rate


@app.delete("/rates/{code}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE — B7: 204
def delete_rate(code: str):
    if code not in RATES_TO_INR:
        raise HTTPException(status_code=404, detail="rate not found")
    RATES_TO_INR.pop(code, None)
    return None


# ====================  /convert  — GET (query) + POST (body)  ====================
@app.get("/convert")  # B3: query params hardened with Query()
def convert(
    amount: float = Query(gt=0, description="Amount in INR"),
    to: Currency = Currency.usd,
):
    return {
        "amount_inr": amount,
        "to": to,
        "converted": round(amount / RATES_TO_INR[to], 2),
    }


@app.post("/convert", response_model=ConversionResult)  # B4 body + B6 response_model
def create_conversion(req: ConversionRequest):
    rate = Decimal(str(RATES_TO_INR[req.to]))
    converted = (Decimal(str(req.amount)) / rate).quantize(Decimal("0.01"))
    return ConversionResult(amount_inr=req.amount, to=req.to, converted=converted)


# ====================  /subscribers  — response_model as a security boundary  ====================
@app.post("/subscribers", response_model=SubscriberPublic, status_code=201)
def create_subscriber(sub: SubscriberIn):
    # Part 07 will hash + store. Here we only show the OUTPUT boundary: password never returns.
    return SubscriberPublic(id=uuid4(), email=sub.email)


# ============================  B9: forms & files  ============================
@app.post("/convert/csv")
async def convert_csv(file: UploadFile):
    content = await file.read()
    lines = content.decode().splitlines()
    return {"filename": file.filename, "rows": len(lines)}


# ============================  B10: headers & cookies  ============================
@app.get("/whoami")
def whoami(
    user_agent: str | None = Header(default=None),
    session: str | None = Cookie(default=None),
):
    return {"user_agent": user_agent, "session": session}
