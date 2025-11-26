import asyncio
from dataclasses import dataclass, replace

import pytest

from pytest_case_provider.case.container import CaseContainer


@dataclass(frozen=True, kw_only=True)
class MyCase:
    foo: int


CASES = CaseContainer[MyCase]()


def test_without_case_injection() -> None:
    assert True


@CASES.inject_func()
def test_case_injected_1(case: MyCase) -> None:
    assert isinstance(case, MyCase), f"case: {type(case)}"
    assert case.foo > 0


@CASES.inject_func()
def test_case_injected_2(case: MyCase, case_foo_inc: MyCase) -> None:
    assert isinstance(case, MyCase), f"case: {type(case)}"
    assert case_foo_inc.foo > case.foo


@CASES.case()
def case_one() -> MyCase:
    return MyCase(foo=1)


@CASES.case()
async def case_two() -> MyCase:
    await asyncio.sleep(0.001)
    return MyCase(foo=2)


@pytest.fixture
def case_foo_inc(
    case: MyCase,  # fixture can use case value
) -> MyCase:
    assert isinstance(case, MyCase), f"case: {type(case)}"
    return replace(case, foo=case.foo + 1)
