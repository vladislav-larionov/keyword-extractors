from dataclasses import dataclass


@dataclass
class Span:
    start: int
    stop: int
    text: str
