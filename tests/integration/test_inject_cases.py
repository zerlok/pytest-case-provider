import asyncio
import typing as t
from dataclasses import dataclass, replace

import pytest

from pytest_case_provider import inject_cases, inject_cases_method


@dataclass(frozen=True, kw_only=True)
class MyCase:
    foo: int


def test_without_case_injection() -> None:
    assert True


@inject_cases
def test_no_case_injected(
    case: MyCase,  # noqa: ARG001
) -> None:
    pytest.fail("this test should not run, because it has no cases")


@inject_cases
def test_case_injected(case: MyCase) -> None:
    assert isinstance(case, MyCase), f"case: {type(case)}"
    assert case.foo > 0


@inject_cases(test_case_injected)  # include cases from other test
def test_cases_included_to_fixture(case: MyCase, case_foo_inc: MyCase) -> None:
    assert isinstance(case, MyCase), f"case: {type(case)}"
    assert case.foo + 1 == case_foo_inc.foo


# this case is for `test_case_injected_to_fixture` only
@test_cases_included_to_fixture.case()
def case_case_minus_one() -> MyCase:
    return MyCase(foo=-1)


@pytest.fixture
def special_number() -> int:
    return 42


@pytest.fixture
def case_foo_inc(
    case: MyCase,  # fixture can use case value
) -> MyCase:
    assert isinstance(case, MyCase), f"case: {type(case)}"
    return replace(case, foo=case.foo + 1)


@test_case_injected.case()
def case_one() -> MyCase:
    return MyCase(foo=1)


@test_case_injected.case()
def case_two() -> MyCase:
    return MyCase(foo=2)


@test_case_injected.case()
async def case_async_three_for_sync_test() -> MyCase:
    await asyncio.sleep(0.01)
    return MyCase(foo=3)


@test_case_injected.case()
def case_yield_four() -> t.Iterator[MyCase]:
    yield MyCase(foo=4)


@test_case_injected.case()
async def case_async_yield_five_for_sync_test() -> t.AsyncIterator[MyCase]:
    await asyncio.sleep(0.01)
    yield MyCase(foo=5)


@test_case_injected.case()
def case_special_number(
    special_number: int,  # case can use values from other fixtures
) -> MyCase:
    return MyCase(foo=special_number)


@test_case_injected.case(
    marks=[
        pytest.mark.skip(reason="test case mark works"),
    ]
)
def case_skipped() -> MyCase:
    pytest.fail("this test should not run, because case provider has skip mark")


class TestClass:
    def test_without_case_injection(self) -> None:
        assert True

    @inject_cases_method
    def test_no_case_injected(self, case: MyCase) -> None:
        pytest.fail("this test should not run, because it has no cases")

    @inject_cases_method
    def test_class_case_injected(self, case: MyCase) -> None:
        assert isinstance(case, MyCase), f"case: {type(case)}"

    @inject_cases_method(test_class_case_injected)
    def test_class_cases_included(self, case: MyCase) -> None:
        assert isinstance(case, MyCase), f"case: {type(case)}"

    @test_class_case_injected.case()
    def case_six(self) -> MyCase:
        return MyCase(foo=6)

    @test_class_case_injected.case()
    def case_seven(self) -> MyCase:
        return MyCase(foo=7)

    @test_class_case_injected.case()
    def case_yield_eight(self) -> t.Iterator[MyCase]:
        yield MyCase(foo=8)

    @test_class_case_injected.case()
    def case_class_special_number(self, special_number: int) -> MyCase:
        return MyCase(foo=special_number)
