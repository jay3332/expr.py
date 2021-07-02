from decimal import Decimal
from rply.token import Token, SourcePosition

from typing import Tuple


__all__: Tuple[str, ...] = (
    'EvaluatorError',
    'CastingError',
    'ParsingError',
    'BadOperation',
    'Overflow',
    'NumberOverflow',
    'ExponentOverflow',
    'FactorialOverflow',
    'InvalidSyntax',
    'UnknownPointer'
)


class EvaluatorError(Exception):
    ...


class CastingError(ValueError, EvaluatorError):
    ...


class ParsingError(EvaluatorError):
    @property
    def friendly(self) -> str:
        return '[ERROR] Could not parse expression properly.'


class BadOperation(ParsingError):
    def __init__(self, operation: str) -> None:
        self.operation: str = operation
        super().__init__(f'invalid operation {operation!r}')

    @property
    def friendly(self) -> str:
        return f'[ERROR] Bad operation {self.operation!r}'


class Overflow(ParsingError):
    @property
    def friendly(self) -> str:
        return f'[OVERFLOW] Overflow'


class NumberOverflow(Overflow):
    def __init__(self, number: Decimal, max_number: Decimal) -> None:
        self.number: Decimal = number
        self.max_number: Decimal = max_number
        super().__init__(f'number {number} surpasses max safe number of {max_number}')

    @property
    def friendly(self) -> str:
        return f'[OVERFLOW] Number {self.number} is too large'


class ExponentOverflow(Overflow):
    def __init__(self, number: Decimal, max_number: Decimal) -> None:
        self.number: Decimal = number
        self.max_number: Decimal = max_number
        super().__init__(f'exponent {number} surpasses max safe exponent of {max_number}')

    @property
    def friendly(self) -> str:
        return f'[OVERFLOW] Exponent {self.number} is too large'


class FactorialOverflow(Overflow):
    def __init__(self, number: Decimal, max_number: Decimal) -> None:
        self.number: Decimal = number
        self.max_number: Decimal = max_number
        super().__init__(f'factorial {number} surpasses max safe factorial of {max_number}')

    @property
    def friendly(self) -> str:
        return f'[OVERFLOW] Factorial {self.number} is too large'


class InvalidSyntax(ParsingError):
    def __init__(self, token: Token) -> None:
        self.token: Token = token
        self.pos: SourcePosition = token.getsourcepos()

        super().__init__(f'invalid token {token.getstr()!r} (line {self.pos.lineno}, col {self.pos.colno})')

    @property
    def friendly(self) -> str:
        return '[ERROR] Invalid syntax'


class UnknownPointer(ParsingError):
    def __init__(self, pointer: str) -> None:
        self.pointer: str = pointer
        super().__init__(f'unknown pointer {pointer!r}')

    @property
    def friendly(self) -> str:
        return f'[ERROR] Variable or function {self.pointer!r} is not found'
