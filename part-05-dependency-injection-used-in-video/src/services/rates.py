"""
The FAT part — business logic only.

No FastAPI imports here on purpose: a service doesn't know it's behind HTTP,
so you can call and test it from anywhere (a script, a test, a CLI).
"""

from decimal import Decimal

RATES_TO_INR: dict[str, float] = {
    "AED": 25.2909,
    "AUD": 61.6076,
    "BDT": 0.7434,
    "BHD": 245.1706,
    "BRL": 15.665,
    "CAD": 64.6718,
    "CHF": 110.2566,
    "CNY": 13.9402,
    "CZK": 4.1457,
    "DKK": 13.5469,
    "EGP": 1.7089,
    "EUR": 101.255,
    "GBP": 121.0568,
    "HKD": 11.8431,
    "HUF": 0.2746,
    "IDR": 0.0051,
    "ILS": 28.1078,
    "INR": 1.0,
    "JPY": 0.5829,
    "KRW": 0.0691,
    "KWD": 297.7716,
    "LKR": 0.2781,
    "MXN": 4.8472,
    "MYR": 22.5549,
    "NOK": 9.449,
    "NPR": 0.6225,
    "NZD": 50.6171,
    "OMR": 241.5843,
    "PHP": 1.4565,
    "PKR": 0.3346,
    "PLN": 22.7679,
    "QAR": 25.3028,
    "RUB": 1.1348,
    "SAR": 24.8054,
    "SEK": 9.0397,
    "SGD": 71.9036,
    "THB": 2.7397,
    "TRY": 1.8347,
    "USD": 92.8809,
    "VND": 0.0036,
    "ZAR": 5.3275,
}


def all_rates() -> dict[str, float]:
    return dict(RATES_TO_INR)


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
