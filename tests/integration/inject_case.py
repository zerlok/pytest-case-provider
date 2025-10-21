"""This module will be invoked via pytester"""

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
    assert isinstance(case, MyCase)


@inject_cases(test_case_injected)
def test_case_increment(case: MyCase, case_foo_inc: MyCase) -> None:
    assert isinstance(case, MyCase)
    assert case.foo + 1 == case_foo_inc.foo


@test_case_increment.case()
def case_case_increment_special() -> MyCase:
    return MyCase(foo=-1)


@pytest.fixture
def number() -> int:
    return 42


@pytest.fixture
def case_foo_inc(case: MyCase) -> MyCase:
    assert isinstance(case, MyCase)
    return replace(case, foo=case.foo + 1)


@test_case_injected.case()
def case_one() -> MyCase:
    return MyCase(foo=1)


@test_case_injected.case()
def case_two() -> MyCase:
    return MyCase(foo=2)


@test_case_injected.case()
def case_number(number: int) -> MyCase:
    return MyCase(foo=number)


class TestClass:
    def test_without_case_injection(self) -> None:
        assert True

    @inject_cases_method
    def test_no_case_injected(self, case: MyCase) -> None:
        pytest.fail("this test should not run, because it has no cases")

    @inject_cases_method
    def test_class_simple(self, case: MyCase) -> None:
        assert isinstance(case, MyCase)

    @test_class_simple.case()
    def case_three(self) -> MyCase:
        return MyCase(foo=3)

    @test_class_simple.case()
    def case_four(self) -> MyCase:
        return MyCase(foo=4)

    @test_class_simple.case()
    def case_class_number(self, number: int) -> MyCase:
        return MyCase(foo=number)
