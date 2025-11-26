import typing as t

from _pytest.mark import MarkDecorator
from typing_extensions import Concatenate, ParamSpec

from pytest_case_provider.case.abc import CaseCollector, CaseRegistry, FuncCaseRegistry, MethodCaseRegistry
from pytest_case_provider.case.configure import configure_testfunc_cases, configure_testmethod_cases
from pytest_case_provider.case.storage import CompositeCaseStorage

U = ParamSpec("U")
T = t.TypeVar("T")
V = t.TypeVar("V")
S = t.TypeVar("S")


class FuncCaseProvider(t.Generic[T]):
    """Provides `FuncCaseRegistry` objects of a specific `T` case type."""

    def __init__(
        self,
        includes: t.Sequence[t.Union[CaseCollector[T], CaseRegistry[T]]],
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> None:
        self.__includes = includes
        self.__marks = marks

    def __call__(self, testfunc: t.Callable[Concatenate[T, U], V]) -> FuncCaseRegistry[T, U, V]:
        return _apply_marks(
            configure_testfunc_cases(testfunc, CompositeCaseStorage[T](), self.__includes),
            self.__marks,
        )


class MethodCaseProvider(t.Generic[T]):
    """Provides `MethodCaseRegistry` objects of a specific `T` case type."""

    def __init__(
        self,
        includes: t.Sequence[t.Union[CaseCollector[T], CaseRegistry[T]]],
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> None:
        self.__includes = includes
        self.__marks = marks

    def __call__(self, testmethod: t.Callable[Concatenate[S, T, U], V]) -> MethodCaseRegistry[S, T, U, V]:
        return _apply_marks(
            configure_testmethod_cases(testmethod, CompositeCaseStorage[T](), self.__includes),
            self.__marks,
        )


class FuncCasePlaceholder:
    """A helper to infer `FuncCaseProvider` type vars when test function is wrapped with python `@` syntax."""

    def __init__(self, marks: t.Optional[t.Sequence[MarkDecorator]] = None) -> None:
        self.__marks = marks

    def __call__(self, testfunc: t.Callable[Concatenate[T, U], V]) -> FuncCaseRegistry[T, U, V]:
        return self.include()(testfunc)

    def include(self, *cases: t.Union[CaseCollector[T], CaseRegistry[T]]) -> FuncCaseProvider[T]:
        return FuncCaseProvider[T](includes=cases, marks=self.__marks)


class MethodCaseStorageProviderPlaceholder:
    """A helper to infer `MethodCaseProvider` type vars when test function is wrapped with python `@` syntax."""

    def __init__(self, marks: t.Optional[t.Sequence[MarkDecorator]] = None) -> None:
        self.__marks = marks

    def __call__(self, testmethod: t.Callable[Concatenate[S, T, U], V]) -> MethodCaseRegistry[S, T, U, V]:
        return self.include()(testmethod)

    def include(self, *cases: t.Union[CaseCollector[T], CaseRegistry[T]]) -> MethodCaseProvider[T]:
        return MethodCaseProvider[T](includes=cases, marks=self.__marks)


def inject_func(
    marks: t.Optional[t.Sequence[MarkDecorator]] = None,
) -> FuncCasePlaceholder:
    """
    Setup case injection into the test function.

    Each wrapped test function will use isolated case storage. Use include to extend cases from other storages.

    :param marks: list of pytest marks to apply on test function (useful when marks are not well annotated for MyPy).
    :return: a placeholder object that can wrap the test function.

    Usage:

    >>> @inject_func()
    ... def test_func(case: str) -> None: # test_func expects cases of type `str`
    ...     assert case == "Foo"
    ...
    >>> @test_func.case() # add case to `test_func` storage
    ... def case_foo() -> str:
    ...     return "Foo"
    ...
    >>> @inject_func().include(test_func) # `test_func_2` includes cases from `test_func`
    ... def test_func_2(case: str) -> None:
    ...     assert case in {"Foo", "Bar"}
    ...
    >>> @test_func_2.case() # add case to `test_func_2` storage
    ... def case_bar() -> str:
    ...     return "Bar"
    """
    return FuncCasePlaceholder(marks)


def inject_method(
    marks: t.Optional[t.Sequence[MarkDecorator]] = None,
) -> MethodCaseStorageProviderPlaceholder:
    """
    Setup case provider injection into the test method.

    Each wrapped test method will use isolated case storage. Use include to extend cases from other storages.

    :param marks: list of pytest marks to apply on test method (useful when marks are not well annotated for MyPy).
    :return: a placeholder object that can wrap the test method.

    Usage:

    >>> class TestClass:
    ...     @inject_method()
    ...     def test_method(self, case: str) -> None: # test_method expects cases of type `str`
    ...         assert case == "Foo"
    ...
    ...     @test_method.case() # add case to `test_method` storage
    ...     def case_foo(self) -> str:
    ...         return "Foo"
    ...
    ...     @inject_method().include(test_method) # `test_method_2` includes cases from `test_method`
    ...     def test_method_2(self, case: str) -> None:
    ...         assert case in {"Foo", "Bar"}
    ...
    ...     @test_method_2.case() # add case to `test_method_2` storage
    ...     def case_bar(self) -> str:
    ...         return "Bar"
    """
    return MethodCaseStorageProviderPlaceholder(marks)


def _apply_marks(func: T, marks: t.Optional[t.Sequence[MarkDecorator]]) -> T:
    for mark in marks or ():
        func = t.cast("T", mark(func))

    return func
