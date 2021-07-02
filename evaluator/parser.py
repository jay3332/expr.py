import math

from decimal import Decimal
from functools import wraps
from rply import ParserGenerator as NativeParserGenerator, Token as _Token
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

from .ast import *
from .util import T as DT
from .errors import BadOperation

T: TypeVar = TypeVar('T')

PT: TypeVar = TypeVar('PT')
RT: TypeVar = TypeVar('RT')

__all__: Tuple[str, ...] = (
    'ParserGeneratorMeta',
)


def rule(pattern: str, precedence: Optional[str] = None) -> Callable[Callable[PT, RT], Callable[PT, RT]]:
    def decorator(func: Callable[PT, RT]) -> Callable[PT, RT]:
        try:
            func.__parser_generator_rules__.append((pattern, precedence))
        except AttributeError:
            func.__parser_generator_rules__ = [(pattern, precedence)]

        return func
    return decorator


def error(func: Callable[PT, RT]) -> Callable[PT, RT]:
    func.__parser_generator_error__ = True
    return func


class ParserGeneratorMeta(type):
    def __new__(mcs, cls: Type[T], bases: Tuple[type, ...], attrs: Dict[str, Any]) -> T:
        def _overwrite_init(__init__):
            @wraps(__init__)
            def __new_init__(self, *args, **kwargs):
                _res = __init__(self, *args, **kwargs)
                if not hasattr(self, '__parser_generator__'):
                    raise TypeError('class must have the "__parser_generator__" attribute')

                pg = self.__parser_generator__
                for member in attrs.items():
                    if hasattr(member, '__parser_generator_rules__'):
                        pg.production(*member.__parser_generator_rules__)(member)

                    elif hasattr(member, '__parser_generator_error__'):
                        pg.error(member)

                return _res
            return __new_init__

        attrs['__init__'] = _overwrite_init(attrs['__init__'])
        return super().__new__(mcs, cls, bases, attrs)


# noinspection PyArgumentList
class ParserGenerator(metaclass=ParserGeneratorMeta):
    def __init__(
            self,
            *,
            max_safe_number: float = 9e9,
            max_exponent: float = 128,
            builtins: Dict[str, Callable[[DT, ...], DT]] = None,
            constants: Dict[str, DT] = None,
            decimal_cls: Type[DT] = Decimal
    ) -> None:
        if not issubclass(decimal_cls, Decimal):
            raise TypeError('decimal_cls must inherit from decimal.Decimal')

        _ = decimal_cls
        self._max_safe_number: DT = _(max_safe_number)
        self._max_exponent: DT = _(max_exponent)

        self._builtins: Dict[str, Callable[[DT, ...], DT]] = {
            'rad': lambda d: _(math.radians(float(d))),
            'sin': lambda d: _(math.sin(float(d))),
            'cos': lambda d: _(math.cos(float(d))),
            'tan': lambda d: _(math.tan(float(d))),
            'asin': lambda d: _(math.asin(float(d))),
            'acos': lambda d: _(math.acos(float(d))),
            'atan': lambda d: _(math.atan(float(d))),
            'log': lambda d: _(math.log(float(d), 2)),
            'log10': lambda d: _(math.log(float(d), 10)),
            'ln': lambda d: _(math.log(float(d))),
            **(builtins or {})
        }

        self._constants: Dict[str, DT] = {
            "pi": _(math.pi),
            "e": _(math.e),
            **(constants or {})
        }

        self._decimal_cls: Type[DT] = decimal_cls

        self.__parser_generator__: NativeParserGenerator = NativeParserGenerator(
            ['NUMBER', 'NAME', 'LPAREN', 'RPAREN', 'ADD', 'SUB', 'MUL',
             'DIV', 'FLOORDIV', 'MOD', 'FACT', 'POW'],
            precedence=[
                ('left', ['ADD', 'SUB']),
                ('left', ['MUL', 'DIV', 'FLOORDIV', 'MOD']),
                ('right', ['POW']),
                ('left', ['FACT'])
            ]
        )

    @rule('expr : NUMBER')
    def number(self, p: List[_Token]) -> Number:
        return Number(p[0].getstr())

    @rule('expr : LPAREN expr RPAREN')
    def paren(self, p: List[_Token]) -> Any:
        return p[1]

    @rule('expr : expr ADD expr')
    @rule('expr : expr SUB expr')
    @rule('expr : expr MUL expr')
    @rule('expr : expr DIV expr')
    @rule('expr : expr FLOORDIV expr')
    @rule('expr : expr MOD expr')
    @rule('expr : expr POW expr')
    @rule('expr : expr FACT')
    def operator(self, p: List[_Token]) -> Any:
        token_type = p[1].gettokentype()

        if token_type == 'FACT':
            return Factorial(p[0])

        try:
            return {
                'ADD': Add,
                'SUB': Sub,
                'MUL': Mul,
                'DIV': Div,
                'FLOORDIV': FloorDiv,
                'MOD': Mod,
                'POW': Pow
            }[token_type](
                p[0], p[2]
            )
        except KeyError:
            raise BadOperation(f'bad operation {token_type!r}')

    def build(self):
        return self.__parser_generator__.build()
