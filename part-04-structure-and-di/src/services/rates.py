"""
The FAT part — business logic only.

No FastAPI imports here on purpose: a service doesn't know it's behind HTTP,
so you can call and test it from anywhere (a script, a test, a CLI).
"""

from decimal import Decimal

RATES_TO_INR: dict[str, float] = {"USD": 83.0, "EUR": 90.0, "GBP": 105.0}


def all_rates(limit: int) -> dict[str, float]:
    return dict(list(RATES_TO_INR.items())[:limit])


def get_rate(code: str) -> float | None:
    return RATES_TO_INR.get(code.upper())


def set_rate(code: str, inr_per_unit: float) -> None:
    RATES_TO_INR[code.upper()] = inr_per_unit


def delete_rate(code: str) -> bool:
    return RATES_TO_INR.pop(code.upper(), None) is not None


def convert(amount_inr: float, to: str) -> Decimal:
    rate = RATES_TO_INR.get(to)
    if rate is None:
        raise KeyError(to)
    return (Decimal(str(amount_inr)) / Decimal(str(rate))).quantize(Decimal("0.01"))
