import math

from decimal import Decimal
from functools import wraps
from warnings import catch_warnings, simplefilter

from rply import ParserGenerator, Token as _Token
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

from rply.lexer import Lexer
from rply.parser import LRParser

from .ast import *
from .errors import *
from .util import T as DT
from .grammar import LexerGenerator

T: TypeVar = TypeVar('T')
LGT: TypeVar = TypeVar('LGT', bound=LexerGenerator)

PT: TypeVar = TypeVar('PT')
RT: TypeVar = TypeVar('RT')

__all__: Tuple[str, ...] = (
    'ParserMeta',
    'Parser'
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


class ParserMeta(type):
    def __new__(mcs, cls: Type[T], bases: Tuple[type, ...], attrs: Dict[str, Any]) -> T:
        def _overwrite_init(__init__):
            @wraps(__init__)
            def __new_init__(self, *args, **kwargs):
                _res = __init__(self, *args, **kwargs)
                if not hasattr(self, '__parser_generator__'):
                    raise TypeError('class must have the "__parser_generator__" attribute')

                pg = self.__parser_generator__
                for member in attrs.values():
                    if hasattr(member, '__parser_generator_rules__'):
                        for rule in member.__parser_generator_rules__:
                            pg.production(*rule)(member)

                    elif hasattr(member, '__parser_generator_error__'):
                        pg.error(member)

                return _res
            return __new_init__

        attrs['__init__'] = _overwrite_init(attrs['__init__'])
        return super().__new__(mcs, cls, bases, attrs)


# noinspection PyArgumentList,PyUnresolvedReferences
class Parser(metaclass=ParserMeta):
    def __init__(
            self,
            *,
            max_safe_number: float = 9e9,
            max_exponent: float = 128,
            max_factorial: float = 64,
            builtins: Dict[str, Callable[[DT, ...], DT]] = None,
            constants: Dict[str, DT] = None,
            variables: Dict[str, DT] = None,
            decimal_cls: Type[DT] = Decimal,
            lexer_cls: Type[LGT] = LexerGenerator
    ) -> None:
        if not issubclass(decimal_cls, Decimal):
            raise TypeError('decimal_cls must inherit from decimal.Decimal')

        _ = decimal_cls
        self._max_safe_number: DT = _(max_safe_number)
        self._max_exponent: DT = _(max_exponent)
        self._max_factorial: DT = _(max_factorial)

        _builtins: Dict[str, Callable[[DT, ...], DT]] = {
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
            'sqrt': lambda d: _(math.sqrt(float(d))),
            'cbrt': lambda d: _(float(d) ** (1 / 3)),
            **(builtins or {})
        }

        _constants: Dict[str, DT] = {
            "pi": _(math.pi),
            "e": _(math.e),
            **(constants or {})
        }

        self._decimal_cls: Type[DT] = decimal_cls

        self.__lexer_generator__: Optional[LGT] = lexer_cls()
        self.__parser_generator__: ParserGenerator = ParserGenerator(
            ['NUMBER', 'NAME', 'LPAREN', 'RPAREN', 'ADD', 'SUB', 'MUL',
             'DIV', 'FLOORDIV', 'MOD', 'FAC', 'POW', 'EQ'],
            precedence=[
                ('left', ['ADD', 'SUB']),
                ('left', ['MUL', 'DIV', 'FLOORDIV', 'MOD']),
                ('right', ['UMINUS']),
                ('right', ['POW']),
                ('left', ['FAC']),
            ]
        )

        self.__lexer__: Optional[Lexer] = None
        self.__parser__: Optional[LRParser] = None

        self._variables: Dict[str, DT] = {
            **_constants,
            **(variables or {})
        }

        self._functions: Dict[str, Callable[[DT, ...], DT]] = _builtins

    @rule('expr : NUMBER')
    def number(self, p: List[_Token]) -> Number:
        number = Number(p[0].getstr())
        if number.eval() > self._max_safe_number:
            raise NumberOverflow(number.eval(), self._max_safe_number)
        return number

    @rule("expr : SUB NUMBER", precedence='UMINUS')
    def uminus(self, p: List[_Token]) -> Any:
        return -(p[1])

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
    @rule('expr : expr FAC')
    def operator(self, p: List[_Token]) -> Any:
        token_type = p[1].gettokentype()

        if token_type == 'FAC':
            if p[0].eval() > self._max_factorial:
                raise FactorialOverflow(p[0].eval(), self._max_factorial)
            return Factorial(p[0])

        try:
            return {
                'ADD': Add,
                'SUB': Sub,
                'MUL': Mul,
                'DIV': Div,
                'FLOORDIV': FloorDiv,
                'MOD': Mod,
            }[token_type](
                p[0], p[2]
            )
        except KeyError:
            if token_type == 'POW':
                if p[2].eval() > self._max_exponent:
                    raise ExponentOverflow(p[2].eval(), self._max_exponent)
                return Pow(p[0], p[2])

            raise BadOperation(token_type)

    @rule('expr : NAME EQ expr')
    def declare(self, p: List[_Token]) -> Any:
        _name = p[0].getstr()
        _value = p[2].eval()
        self._variables[_name] = _value

    @rule('expr : NAME LPAREN expr RPAREN')
    def function(self, p: List[_Token]) -> Any:
        _name = p[0].getstr()
        if _name in self._functions:
            _value = p[2].eval()
            return Number(self._functions[_name](_value))

        return Mul(self.getvar(p[0]), p[2])  # Probably this instead

    @rule('expr : NAME')
    def getvar(self, p: List[_Token]) -> Any:
        name = p[0].getstr()

        try:
            return Number(self._variables[name])
        except KeyError:
            raise UnknownPointer(name)

    @rule('expr : expr expr', precedence='MUL')
    def shortmul(self, p: List[_Token]) -> Any:
        return Mul(p[0], p[1])

    @error
    def on_error(self, token: _Token) -> Any:
        raise InvalidSyntax(token)

    def _build(self) -> LRParser:
        self.__parser__ = res = self.__parser_generator__.build()
        return res

    def _build_lexer(self) -> Lexer:
        self.__lexer__ = res = self.__lexer_generator__.build()
        return res

    def evaluate(self, expr: str) -> float:
        with catch_warnings():
            simplefilter('ignore')
            parser = self.__parser__ or self._build()
            lexer = self.__lexer__ or self._build_lexer()

        result = parser.parse(lexer.lex(expr), state=self)
        if result is not None:
            return result.eval()