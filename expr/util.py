from typing import Tuple, Type, TypeVar
from decimal import Decimal, DecimalException

T: TypeVar = TypeVar('T', bound=Decimal)

__all__: Tuple[str, ...] = (
    'cast',
    'T'
)


def cast(number: str, /, *, cls: Type[T] = Decimal) -> T:
    try:
        return cls(number)
    except DecimalException:
        return None
