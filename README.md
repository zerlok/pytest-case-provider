# pytest-case-provider

[![Latest Version](https://img.shields.io/pypi/v/pytest-case-provider.svg)](https://pypi.python.org/pypi/pytest-case-provider)
[![Python Supported Versions](https://img.shields.io/pypi/pyversions/pytest-case-provider.svg)](https://pypi.python.org/pypi/pytest-case-provider)
[![MyPy Strict](https://img.shields.io/badge/mypy-strict-blue)](https://mypy.readthedocs.io/en/stable/getting_started.html#strict-mode-and-configuration)
[![Test Coverage](https://codecov.io/gh/zerlok/pytest-case-provider/branch/main/graph/badge.svg)](https://codecov.io/gh/zerlok/pytest-case-provider)
[![Downloads](https://img.shields.io/pypi/dm/pytest-case-provider.svg)](https://pypistats.org/packages/pytest-case-provider)
[![GitHub stars](https://img.shields.io/github/stars/zerlok/pytest-case-provider)](https://github.com/zerlok/pytest-case-provider/stargazers)

Lightweight case parametrization for `pytest` with **fixture**, **class**, and **async** support.
Provides **declarative**, **typed** case injection for both sync and async test functions.

---

## Installation

```bash
pip install pytest-case-provider
````

---

## Overview

`pytest-case-provider` extends pytest’s parametrization system.  
It was **inspired by** [`pytest-cases`](https://smarie.github.io/python-pytest-cases/), but redesigned from scratch for **strict typing**, **async support**, and **fixture-native case injection**.

It allows attaching *case providers* directly to test functions or methods via `@inject_cases` and  
`@inject_cases_method`.

Cases can be:

* Synchronous or asynchronous.
* Iterable or async-iterable.
* Fixture-dependent.
* Composable across tests or classes.

---

## API Summary

| Symbol                    | Description                           |
|---------------------------|---------------------------------------|
| `inject_cases`            | Decorator/injector for test functions |
| `inject_cases_method`     | Same as above, for test class methods |
| `CaseStorage[T]`          | Mutable case storage container        |
| `CompositeCaseStorage[T]` | Aggregates multiple `CaseCollector`   |

---

## Example

```python
import typing
from dataclasses import dataclass, replace
import pytest
from pytest_case_provider import inject_cases, inject_cases_method


@dataclass(frozen=True, kw_only=True)
class MyCase:
    foo: int


@pytest.fixture
def number() -> int:
    return 42


# Regular test
def test_without_case_injection() -> None:
    assert True


# Case-enabled test function
@inject_cases
def test_case_injected(case: MyCase) -> None:
    assert isinstance(case, MyCase)


# Cross-inject from another test
@inject_cases(test_case_injected)
def test_case_increment(case: MyCase, case_foo_inc: MyCase) -> None:
    assert case.foo + 1 == case_foo_inc.foo


# Define case providers
@test_case_injected.case()
def case_one() -> MyCase:
    return MyCase(foo=1)


@test_case_injected.case()
def case_two() -> MyCase:
    return MyCase(foo=2)


# Use other fixtures in case providers
@test_case_injected.case()
def case_number(number: int) -> MyCase:
    return MyCase(foo=number)


# Async case provider
@test_case_injected.case()
async def case_async_generated() -> MyCase:
    return MyCase(foo=999)


# Iterable provider
@test_case_injected.case()
def case_iterable() -> typing.Iterator[MyCase]:
    yield MyCase(foo=10)


# Async iterable provider
@test_case_injected.case()
async def case_async_iterable() -> typing.Iterator[MyCase]:
    yield MyCase(foo=20)


# Access case object from fixture
@pytest.fixture
def case_foo_inc(case: MyCase) -> MyCase:
    return replace(case, foo=case.foo + 1)


# Example class-based usage
class TestClass:
    @inject_cases_method
    def test_class_cases(self, case: MyCase) -> None:
        assert isinstance(case, MyCase)

    @test_class_cases.case()
    def case_three(self) -> MyCase:
        return MyCase(foo=3)

    @test_class_cases.case()
    def case_four(self) -> MyCase:
        return MyCase(foo=4)
```

## Test Discovery Output

Pytest will expand each injected case as a distinct test variant using pytest's parametrization:

```
test_example.py::test_case_injected[case_one] PASSED
test_example.py::test_case_injected[case_two] PASSED
test_example.py::test_case_injected[case_number] PASSED
test_example.py::test_case_injected[case_async_generated] PASSED
test_example.py::test_case_injected[case_iterable] PASSED
test_example.py::test_case_injected[case_async_iterable] PASSED
test_example.py::test_case_increment[case_one] PASSED
test_example.py::test_case_increment[case_two] PASSED
test_example.py::test_case_increment[case_number] PASSED
test_example.py::test_case_increment[case_async_generated] PASSED
test_example.py::test_case_increment[case_iterable] PASSED
test_example.py::test_case_increment[case_async_iterable] PASSED
test_example.py::TestClass::test_class_cases[case_three] PASSED
test_example.py::TestClass::test_class_cases[case_four] PASSED
```
