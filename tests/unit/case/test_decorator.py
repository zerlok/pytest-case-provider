import pytest

from pytest_case_provider.case.decorator import TestFuncCaseDecorator, TestMethodCaseDecorator


def test_test_func_case_decorator_to_str(
    my_test_func_decorator: TestFuncCaseDecorator[[], None, int],
) -> None:
    assert my_test_func.__name__ in str(my_test_func_decorator)


def test_test_method_case_decorator_to_str(
    my_test_method_decorator: TestMethodCaseDecorator[[], None, int, "MyTestClass"],
) -> None:
    assert MyTestClass.my_test_func.__name__ in str(my_test_method_decorator)


def my_test_func(my_case: int) -> None:
    pass


class MyTestClass:
    def my_test_func(self, my_case: int) -> None:
        pass


@pytest.fixture
def my_test_func_decorator() -> TestFuncCaseDecorator[[], None, int]:
    return TestFuncCaseDecorator(my_test_func)


@pytest.fixture
def my_test_method_decorator() -> TestMethodCaseDecorator[[], None, int, MyTestClass]:
    return TestMethodCaseDecorator(MyTestClass.my_test_func)
