from typing import Optional, Tuple
from .parser import Parser

__all__: Tuple[str, ...] = (
    'evaluate',
    'create_state',
    'state'
)

state: Optional[Parser] = None


def evaluate(expr: str, **kwargs) -> float:
    global state

    if not state:
        state = Parser(**kwargs)

    return state.evaluate(expr)


def create_state(**kwargs) -> Parser:
    return Parser(**kwargs)
