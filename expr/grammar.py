import re

from typing import Tuple
from rply import LexerGenerator as _BaseGenerator

__all__: Tuple[str, ...] = (
    'LexerGenerator',
)


class LexerGenerator(_BaseGenerator):
    """
    Generates the lexer used to parse inputs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.add_all()

    def add_all(self) -> None:
        self.add_ignores()
        self.add_basic()
        self.add_operations()

    def add_ignores(self) -> None:
        self.ignore(r'\s+')  # Whitespace
        self.ignore(r'\n+')  # Newlines
        self.ignore(r'#\s*\[.*\]', re.S)  # Multi-line/inline comments
        self.ignore(r'#.*')  # Comments

    def add_basic(self) -> None:
        self.add('NUMBER', r'-?([0-9]+(\.[0-9]*)?|\.[0-9]+)')
        self.add('NAME', r'[a-zA-Z_][a-zA-Z0-9_]*')
        self.add('LPAREN', r'\(')
        self.add('RPAREN', r'\)')
        self.add('LBRACE', r'\{')
        self.add('RBRACE', r'\}')

    def add_operations(self) -> None:
        self.add('ADD', r'\+')
        self.add('SUB', '-')
        self.add('MUL', r'\*')
        self.add('FLOORDIV', '//')
        self.add('DIV', '/')
        self.add('POW', r'\^')
        self.add('FAC', '!')
        self.add('MOD', '%')
        self.add('EQ', '=')
