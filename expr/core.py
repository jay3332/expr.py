from decimal import Decimal
from typing import Optional, Tuple, Type, TypeVar, Union

from .parser import Parser


C = TypeVar('C', bound=Union[float, Decimal])


__all__: Tuple[str, ...] = (
    'evaluate',
    'create_state',
    'state'
)

state: Optional[Parser] = None


def evaluate(expr: str, /, *, cls: Type[C] = Decimal, **kwargs) -> C:
    global state

    if not state:
        state = Parser(**kwargs)

    return state.evaluate(expr, cls=cls)


def create_state(**kwargs) -> Parser:
    return Parser(**kwargs)
