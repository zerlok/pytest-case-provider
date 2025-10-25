import pytest

from pytest_case_provider.case.decorator import FuncCaseDecorator, MethodCaseDecorator


def test_test_func_case_decorator_to_str(
    my_test_func_decorator: FuncCaseDecorator[[], None, int],
) -> None:
    assert str(my_test_func) in str(my_test_func_decorator)


def test_test_method_case_decorator_to_str(
    my_test_method_decorator: MethodCaseDecorator[[], None, int, "MyTestClass"],
) -> None:
    assert str(MyTestClass.my_test_func) in str(my_test_method_decorator)


def my_test_func(my_case: int) -> None:
    pass


class MyTestClass:
    def my_test_func(self, my_case: int) -> None:
        pass


@pytest.fixture
def my_test_func_decorator() -> FuncCaseDecorator[[], None, int]:
    return FuncCaseDecorator(my_test_func)


@pytest.fixture
def my_test_method_decorator() -> MethodCaseDecorator[[], None, int, MyTestClass]:
    return MethodCaseDecorator(MyTestClass.my_test_func)
