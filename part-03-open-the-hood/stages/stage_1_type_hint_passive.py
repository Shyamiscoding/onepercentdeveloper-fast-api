"""
STAGE 1 (notes A1) — a type hint only DESCRIBES; it does NOT enforce.

A plain function with a `: float` hint will happily accept a string. Python
ignores the hint at runtime — you only get an error LATER, when some operation
trips on the wrong type (or, worse, no error at all). The lesson: the hint is
passive; Pydantic (next stages) is what actually enforces it.

Run:  uv run python stages/stage_1_type_hint_passive.py
"""


def convert(amount: float) -> float:
    return amount / 83.0


print("STAGE 1 — the hint is passive")

# 1) the hint says `float`, but Python runs it with a string anyway...
try:
    print(convert("not a number"))
except TypeError as e:
    print(f"   -> TypeError, but ONLY at the math: {e!r}")
    print("      the ': float' hint never fired.")


# 2) sometimes there is NO error at all — just a silently wrong result
def label(name: str) -> str:
    return name * 3


# `!r` shows repr() so the TYPE is visible: a str would print WITH quotes ('15'), but an int prints WITHOUT (15) -> proof the '-> str' hint never fired
print(f"   label(5) = {label(5)!r}   <- passed an int, got '15' (silently wrong!)")
print("   => a hint DESCRIBES; it never ENFORCES. That is Pydantic's job.")
