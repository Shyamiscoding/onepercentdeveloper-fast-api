"""
STAGE 1 (notes 01 + 02) — your function, TRAPPED.

A perfectly good function. But:
    - it only runs when YOU run this file
    - it runs once, prints, and the program EXITS
    - nobody else (a phone app, a website, a friend) can call it

To set it free it needs two things it doesn't have:
    (1) ALWAYS ON          — keep running, waiting
    (2) LISTEN + RESPOND   — accept a request over the network, send an answer back
That's a server's job. Stage 2 brings one in: uvicorn.

Run:  uv run python stages/stage_1_plain_function.py
"""


def convert_inr_to_usd(amount):
    return {"usd": amount / 83.0}


print(convert_inr_to_usd(8300))  # {'usd': 100.0}  — and then the program is gone
