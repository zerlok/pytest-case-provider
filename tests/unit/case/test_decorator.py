import typing as t

import pytest

from pytest_case_provider.case.decorator import FuncCaseStorage, MethodCaseStorage


def test_test_func_case_decorator_to_str(
    my_test_func_decorator: FuncCaseStorage[t.Any, None, int],
) -> None:
    assert str(my_test_func) in str(my_test_func_decorator)


def test_test_method_case_decorator_to_str(
    my_test_method_decorator: MethodCaseStorage[t.Any, None, int, "MyTestClass"],
) -> None:
    assert str(MyTestClass.my_test_func) in str(my_test_method_decorator)


def my_test_func(my_case: int) -> None:
    pass


class MyTestClass:
    def my_test_func(self, my_case: int) -> None:
        pass


@pytest.fixture
def my_test_func_decorator() -> FuncCaseStorage[t.Any, None, int]:
    return FuncCaseStorage(my_test_func)


@pytest.fixture
def my_test_method_decorator() -> MethodCaseStorage[t.Any, None, int, MyTestClass]:
    return MethodCaseStorage(MyTestClass.my_test_func)
