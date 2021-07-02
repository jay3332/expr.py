from .grammar import LexerGenerator
from .parser import ParserGenerator


def evaluate(expr: str) -> float:
    lexer = LexerGenerator().build()
    parser = ParserGenerator().build()

    return parser.parse(lexer.lex(expr)).eval()
