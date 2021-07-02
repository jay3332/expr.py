import math

from decimal import Decimal
from rply.token import BaseBox
from abc import ABC, abstractmethod
from typing import Generic, Tuple, TypeVar

from .errors import CastingError
from .util import cast


ET: TypeVar = TypeVar('NT', bound=Decimal)

__all__: Tuple[str, ...] = (
    'Token',
    'Number',
    'Operator',
    'Add',
    'Sub',
    'Mul',
    'Div',
    'Mod',
    'FloorDiv',
    'Pow',
    'Factorial'
)


class Token(ABC, BaseBox, Generic[ET]):
    @abstractmethod
    def eval(self) -> ET:
        raise NotImplementedError


class Number(Token):
    __slots__ = '_value',

    def __init__(self, value: str) -> None:
        _casted = cast(value)
        if _casted is None:
            raise CastingError(f'could not cast {value!r} to a number.')
        else:
            self._value: ET = _casted

    def eval(self) -> ET:
        return self._value


class Operator(Token):
    __slots__ = '_left', '_right'

    def __init__(self, left: Token[ET], right: Token[ET]) -> None:
        self._left: Token[ET] = left
        self._right: Token[ET] = right

    def eval(self) -> ET:
        raise NotImplementedError


class Add(Operator):
    def eval(self) -> ET:
        return self._left.eval() + self._right.eval()


class Sub(Operator):
    def eval(self) -> ET:
        return self._left.eval() - self._right.eval()


class Mul(Operator):
    def eval(self) -> ET:
        return self._left.eval() * self._right.eval()


class Div(Operator):
    def eval(self) -> ET:
        return self._left.eval() / self._right.eval()


class FloorDiv(Operator):
    def eval(self) -> ET:
        return self._left.eval() // self._right.eval()


class Mod(Operator):
    def eval(self) -> ET:
        return self._left.eval() % self._right.eval()


class Pow(Operator):
    def eval(self) -> ET:
        return self._left.eval() ** self._right.eval()


class Factorial(Token):
    __slots__ = '_left',

    def __init__(self, left: Token[ET]) -> None:
        self._left: Token[ET] = left

    def eval(self) -> ET:
        try:
            return cast(math.factorial(int(self._left)))
        except ValueError:
            return cast(0)
