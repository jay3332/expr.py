<h1 align="center">
    expr.py
</h1>
<p align="center">
    <sup>
        A safe and simple math evaluator for Python, built with rply.
        <br />
        <a href="https://pypi.org/project/expr.py/">
            <b>View on PyPI</b>
        </a>
    </sup>
</p>

Expr.py is a simple but safe math expression evaluator made for Python.   
It can evaluate pretty advanced math concepts without crashing your computer.

Made using [rply](https://github.com/alex/rply/)

## Features
- Fully object oriented
- Completely typed for intellisense
- Protection against DoS attacks
- Customizable and extendable
- Follows order of operations
- Floating point precision

## Getting started
You should install expr.py using `pip`:
```sh 
$ pip install -U expr.py
```

Here is a simple program to get started:
```py 
import expr

if __name__ == '__main__':
    expression = '6 + 5 * 2' 
    print(expr.evaluate(expression))  # 16
```

## What does expr.py support?
### Basic operations
The following operations are supported by expr.py:
- `+` (addition)
- `-` (subtraction)
- `*` (multiplication)
- `/` (division)
- `//` (floor division)
- `%` (modulo)
- `^` (exponentation)
- `!` (factorial)

### Variables
The most basic way of defining variables is by 
passing in the `variables` kwarg into the evaluator.
```py 
expr.evaluate('2x', variables={'x': 2})  # 4
```

You can also let the input define variables:
```py 
expr.evaluate('x = 5')
expr.evaluate('6 + x')  # 11
```

There are by default, 2 predefined constants. (`pi` and `e`)

### Functions [WIP]
You can define functions through the `builtins` kwarg:
```py 
def f(x):
    return x + 1

expr.evaluate('f(5)', builtins={'f': f})  # 6
```

You can also define functions via input: 
```py 
expr.evaluate('f(x) = 2x')
expr.evaluate('f(3)')  # 6
```

There are a few builtin functions:
- `sqrt`
- `cbrt`
- `log`
- `log10`
- `ln`
- `rad`
- `sin`
- `cos`
- `tan`
- `asin`
- `acos`
- `atan`

### Grouping
This concept is pretty simple, anything in parentheses will be evaluated 
before anything outside of them.

```py 
expr.evaluate('5 * 6 + 2')  # 32
expr.evaluate('5 * (6 + 2)')  # 40
```

### States
You can create different states so that each can store their
 own variables and functions independently from others.
 
 To do this, use `expr.create_state`:
```py 
state = expr.create_state()
print(state.evaluate('0.1 + 0.2'))  # 0.3 
```

*Note: All parameters belong in `create_state` rather than in `evaluate` for states.*

Again, variables and functions are independent from each other:
```py 
state1 = expr.create_state()
state1.evaluate('x = 1')

state2 = expr.create_state()
state2.evaluate('x')  # error (x is not defined)

state1.evaluate('x')  # 1
```
