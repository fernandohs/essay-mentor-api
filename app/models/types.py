from typing import Literal

MAX_LEN = 8000

Section = Literal[
    "claim", "reasoning", "evidence", "backing", "reservation", "rebuttal"
]

Rating = Literal["excellent", "good", "fair", "poor"]

