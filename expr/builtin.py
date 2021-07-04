from decimal import Decimal, getcontext
from typing import Callable, Tuple, TypeVar
from functools import wraps


DT: TypeVar = TypeVar('DT', bound=Decimal)


__all__: Tuple[str, ...] = (
    'e',
    'pi',
    'phi',
    'tau',
    'sin',
    'cos'
)


# Common constants
e: Decimal = Decimal('2.718281828459045235360287471352662497757247')
pi: Decimal = Decimal('3.141592653598979323846264338327950288419716')
phi: Decimal = Decimal('1.618033988749894848204586834365638117720309')
tau: Decimal = Decimal('6.283185307179586476925286766559005768394338')

one_third: Decimal = Decimal('0.33333333333333333333333333333333333333333')
one_sixth: Decimal = Decimal('0.16666666666666666666666666666666666666667')


# https://docs.python.org/3/library/decimal.html#recipes

def _modulate_first(func: Callable[[DT], DT]) -> Callable[[DT], DT]:
    @wraps(func)
    def inner(x: DT, /) -> DT:
        if x > tau:
            x %= tau
        return func(x)

    return inner


@_modulate_first
def sin(x: DT, /) -> DT:
    getcontext().prec += 2

    x_squared = x * x
    i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1

    while s != lasts:
        lasts = s
        i += 2
        fact *= i * (i - 1)
        num *= x_squared
        sign *= -1
        s += num / fact * sign

    getcontext().prec -= 2
    return +s


@_modulate_first
def cos(x: DT, /) -> DT:
    getcontext().prec += 2

    x_squared = x * x
    i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1

    while s != lasts:
        lasts = s
        i += 2
        fact *= i * (i-1)
        num *= x_squared
        sign *= -1
        s += num / fact * sign

    getcontext().prec -= 2
    return +s
