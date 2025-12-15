# pytest-case-provider

[![Latest Version](https://img.shields.io/pypi/v/pytest-case-provider.svg)](https://pypi.python.org/pypi/pytest-case-provider)
[![Python Supported Versions](https://img.shields.io/pypi/pyversions/pytest-case-provider.svg)](https://pypi.python.org/pypi/pytest-case-provider)
![Pytest versions](https://img.shields.io/badge/pytest-8%20%7C%209-blue)
[![MyPy Strict](https://img.shields.io/badge/mypy-strict-blue)](https://mypy.readthedocs.io/en/stable/getting_started.html#strict-mode-and-configuration)
[![Test Coverage](https://codecov.io/gh/zerlok/pytest-case-provider/branch/main/graph/badge.svg)](https://codecov.io/gh/zerlok/pytest-case-provider)
[![Downloads](https://img.shields.io/pypi/dm/pytest-case-provider.svg)](https://pypistats.org/packages/pytest-case-provider)
[![GitHub stars](https://img.shields.io/github/stars/zerlok/pytest-case-provider)](https://github.com/zerlok/pytest-case-provider/stargazers)

Parametrization for pytest with fixture support, async support, class-method support, shared storage, and module-level case discovery. Declarative, typed, on-demand injection for sync, async, iterable, and async-iterable providers.

---
## Overview

Extends pytest’s parametrization layer with case storages and containers. Containers attach case sets to test functions and test methods via `inject_func` and `inject_method`. Fixtures integrate natively. Async is supported. Matching `case_*.py` modules are scanned and loaded. Duplicate case names collapse to single instances.

---

## Core Concepts

### Providers

Functions that yield case values. Supported forms:

* Sync
* Async
* Iterable
* Async iterable
* Fixture-dependent

### Storage

`CaseStorage` instances hold providers. `CompositeCaseStorage` merges multiple storages.

### Container

`CaseContainer` wraps a storage and exposes:

* `.case()`
* `.include()`
* `.inject_func()`
* `.inject_method()`

A single container instance feeds any number of tests.

### Injectors

`inject_func()` and `inject_method()` create isolated containers for direct use. `.include()` attaches external storages to them.

### Module-Level Loading

If `test_x.py` exists alongside `case_x.py`, the plugin imports the case module and registers its providers. Tests using `inject_func()` or `inject_method()` receive matching providers. Matching is based on the type annotation of the `case` parameter.

---

## Installation

```bash
pip install pytest-case-provider
```

---

## Quick Start

```python
# test_example.py
import typing
from dataclasses import dataclass
from pytest_case_provider import CaseContainer

@dataclass(frozen=True)
class MyCase:
    foo: int

container = CaseContainer[MyCase]()

@container.inject_func()
def test_cases(case: MyCase) -> None:
    assert isinstance(case, MyCase)

class TestGroup:
    @container.inject_method()
    def test_group(self, case: MyCase) -> None:
        assert case.foo >= 1

@container.case()
def case_small() -> MyCase:
    return MyCase(foo=1)

@container.case()
async def case_async() -> MyCase:
    return MyCase(foo=999)

@container.case()
def case_range() -> typing.Iterator[MyCase]:
    yield MyCase(foo=10)
```

---

## Module-Level Case Files

```
tests/
    test_math.py
    case_math.py
```

`case_math.py`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class MathCase:
    x: int
    y: int

def case_x1_y2() -> MathCase:
    return MathCase(1, 2)
```

`test_math.py`:

```python
from pytest_case_provider import inject_func
from tests.case_math import MathCase

@inject_func()
def test_add(case: MathCase) -> None:
    assert case.x + case.y == 3
```

The plugin imports `case_math` and binds its providers to the injector.

---

## Pytest Expansion

```
test_example.py::test_cases[case_small]
test_example.py::test_cases[case_async]
test_example.py::test_cases[case_range0]
test_example.py::test_cases[case_range1]
test_example.py::TestGroup::test_group[case_small]
test_example.py::TestGroup::test_group[case_async]
test_example.py::TestGroup::test_group[case_range0]
test_example.py::TestGroup::test_group[case_range1]
```

---

## Notes

* Async requires `pytest-asyncio`.
* AnyIO execution paths are disabled.
* Case deduplication follows provider-name semantics.
