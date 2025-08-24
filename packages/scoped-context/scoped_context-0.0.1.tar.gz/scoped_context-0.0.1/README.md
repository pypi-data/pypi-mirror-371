# scoped-context

[![PyPI](https://img.shields.io/pypi/v/scoped-context)](https://pypi.org/project/scoped-context/)
![PyPI - License](https://img.shields.io/pypi/l/scoped-context)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/scoped-context)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![PyPI - Downloads](https://img.shields.io/pypi/dm/scoped-context)

`scoped-context` helps manage scopes using context managers in Python.

## Installation

```bash
pip install scoped-context
```

or

```bash
uv add scoped-context
```

## Usage

Get the context stack and current context of a specific class:

```python
from scoped_context import ScopedContext

class A(ScopedContext):
    pass

with A() as a1:
    print(A.context_stack())  # -> `[a1]`
    print(A.current())  # -> `a1`

    with A() as a2:
        print(A.context_stack())  # -> `[a1, a2]`
        print(A.current())  # -> `a2`

    print(A.context_stack())  # -> `[a1]`
    print(A.current())  # -> `a1`

print(A.context_stack())  # -> `[]`
print(A.current())  # -> raises scoped_context.NoContextError
```

You can mix different subclasses of `ScopedContext`, and access the class-wide context:

```python
from scoped_context import ScopedContext, get_current_context, get_context_stack

class A(ScopedContext):
    pass

class B(ScopedContext):
    pass

class C(ScopedContext):
    pass

with A() as a1:
    with B() as b1:
        with C() as c1:
            # class-wide context
            print(get_context_stack())  # -> `[a1, b1, c1]`
            print(get_current_context())  # -> `c1`

            # You can specify classes (recommended)
            print(get_context_stack((A, B)))  # -> `[a1, b1]`
            print(get_current_context((A, B)))  # -> `b1`

            # class-specific context
            print(A.context_stack())  # -> `[a1]`
            print(A.current())  # -> `a1`
            print(B.context_stack())  # -> `[b1]`
            print(B.current())  # -> `b1`
            print(C.context_stack())  # -> `[c1]`
            print(C.current())  # -> `c1`
```
