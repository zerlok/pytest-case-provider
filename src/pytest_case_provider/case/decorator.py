import inspect
import typing as t

from _pytest.mark import MarkDecorator
from typing_extensions import Concatenate, ParamSpec

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.storage import (
    CaseConfig,
    CaseConfigHolder,
    CompositeCaseStorage,
    FuncCaseStorage,
    MethodCaseStorage,
)

U = ParamSpec("U")
T = t.TypeVar("T")
V = t.TypeVar("V")
S = t.TypeVar("S")


class FuncDecorator:
    def __init__(
        self,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> None:
        self.__marks = marks

    def apply(self, func: T) -> T:
        for mark in self.__marks or ():
            func = t.cast("T", mark(func))

        return func


class FuncCaseStorageProvider(t.Generic[T]):
    """Provides `FuncCaseStorage` objects of a specific `T` case type."""

    def __init__(
        self,
        decorators: FuncDecorator,
        includes: t.Sequence[t.Union[CaseCollector[T], CaseConfigHolder[T]]],
    ) -> None:
        self.__decorators = decorators
        self.__includes = includes

    def __call__(self, testfunc: t.Callable[Concatenate[T, U], V]) -> FuncCaseStorage[T, U, V]:
        wrapped = wrap_testfunc_cases(testfunc)
        include_cases(wrapped, self.__includes)
        return self.__decorators.apply(wrapped)


class MethodCaseStorageProvider(t.Generic[T]):
    """Provides `MethodCaseStorage` objects of a specific `T` case type."""

    def __init__(
        self,
        decorators: FuncDecorator,
        includes: t.Sequence[t.Union[CaseCollector[T], CaseConfigHolder[T]]],
    ) -> None:
        self.__decorators = decorators
        self.__includes = includes

    def __call__(self, testmethod: t.Callable[Concatenate[S, T, U], V]) -> MethodCaseStorage[S, T, U, V]:
        wrapped = wrap_testmethod_cases(testmethod)
        include_cases(wrapped, self.__includes)
        return self.__decorators.apply(wrapped)


class FuncCaseStorageProviderPlaceholder:
    """A helper to infer `FuncCaseStorageProvider` type vars when test function is wrapped with python `@` syntax."""

    def __init__(self, decorators: FuncDecorator) -> None:
        self.__decorators = decorators

    def __call__(self, testfunc: t.Callable[Concatenate[T, U], V]) -> FuncCaseStorage[T, U, V]:
        return self.include()(testfunc)

    def include(self, *others: t.Union[CaseCollector[T], CaseConfigHolder[T]]) -> FuncCaseStorageProvider[T]:
        return FuncCaseStorageProvider[T](decorators=self.__decorators, includes=others)


class MethodCaseStorageProviderPlaceholder:
    """A helper to infer `MethodCaseStorageProvider` type vars when test function is wrapped with python `@` syntax."""

    def __init__(self, decorators: FuncDecorator) -> None:
        self.__decorators = decorators

    def __call__(self, testmethod: t.Callable[Concatenate[S, T, U], V]) -> MethodCaseStorage[S, T, U, V]:
        return self.include()(testmethod)

    def include(self, *others: t.Union[CaseCollector[T], CaseConfigHolder[T]]) -> MethodCaseStorageProvider[T]:
        return MethodCaseStorageProvider[T](decorators=self.__decorators, includes=others)


def inject_cases_func(
    marks: t.Optional[t.Sequence[MarkDecorator]] = None,
) -> FuncCaseStorageProviderPlaceholder:
    """
    Setup case provider injection into the test function.

    :param marks: list of pytest marks to apply on test function (useful when marks are not well annotated for MyPy).
    :return: a placeholder object that can wrap the test function.

    Usage:

    >>> @inject_cases_func()
    ... def test_func(case: str) -> None: # test_func expects cases of type `str`
    ...     assert case == "Foo"
    ...
    >>> @test_func.case() # add case to `test_func` storage
    ... def case_foo() -> str:
    ...     return "Foo"
    ...
    >>> @inject_cases_func.include(test_func) # `test_func_2` includes cases from `test_func`
    ... def test_func_2(case: str) -> None:
    ...     assert case in {"Foo", "Bar"}
    ...
    >>> @test_func_2.case() # add case to `test_func_2` storage
    ... def case_bar() -> str:
    ...     return "Bar"
    """
    return FuncCaseStorageProviderPlaceholder(FuncDecorator(marks))


def inject_cases_method(
    marks: t.Optional[t.Sequence[MarkDecorator]] = None,
) -> MethodCaseStorageProviderPlaceholder:
    """
    Setup case provider injection into the test method.

    :param marks: list of pytest marks to apply on test method (useful when marks are not well annotated for MyPy).
    :return: a placeholder object that can wrap the test method.

    Usage:

    >>> class TestClass:
    ...     @inject_cases_method()
    ...     def test_method(self, case: str) -> None: # test_method expects cases of type `str`
    ...         assert case == "Foo"
    ...
    ...     @test_method.case() # add case to `test_method` storage
    ...     def case_foo(self) -> str:
    ...         return "Foo"
    ...
    ...     @inject_cases_method.include(test_method) # `test_method_2` includes cases from `test_method`
    ...     def test_method_2(self, case: str) -> None:
    ...         assert case in {"Foo", "Bar"}
    ...
    ...     @test_method_2.case() # add case to `test_method_2` storage
    ...     def case_bar(self) -> str:
    ...         return "Bar"
    """
    return MethodCaseStorageProviderPlaceholder(FuncDecorator(marks))


def wrap_testfunc_cases(
    testfunc: t.Callable[Concatenate[T, U], V],
) -> FuncCaseStorage[T, U, V]:
    config = CaseConfig(
        storage=CompositeCaseStorage[T](),
        case_parameter=next(iter(inspect.signature(testfunc).parameters.values())),
    )

    wrapped = t.cast("FuncCaseStorage[T, U, V]", testfunc)
    wrapped.__pytest_case_config__ = config
    wrapped.case = config.storage.case  # type: ignore[method-assign]
    wrapped.include = config.storage.include  # type: ignore[method-assign,assignment]

    return wrapped


def wrap_testmethod_cases(
    testmethod: t.Callable[Concatenate[S, T, U], V],
) -> MethodCaseStorage[S, T, U, V]:
    params = iter(inspect.signature(testmethod).parameters.values())
    next(params)  # skip `self`

    config = CaseConfig(
        storage=CompositeCaseStorage[T](),
        case_parameter=next(params),
    )

    wrapped = t.cast("MethodCaseStorage[S, T, U, V]", testmethod)
    wrapped.__pytest_case_config__ = config
    wrapped.case = config.storage.case  # type: ignore[method-assign]
    wrapped.include = config.storage.include  # type: ignore[method-assign,assignment]

    return wrapped


def include_cases(
    storage: CaseConfigHolder[T],
    includes: t.Optional[t.Sequence[t.Union[CaseCollector[T], CaseConfigHolder[T], None]]],
) -> None:
    config: t.Optional[CaseConfig[T]] = extract_case_config(storage)
    if config is None:
        return

    for include in includes or ():
        sub: t.Optional[CaseCollector[T]] = (
            include
            if isinstance(include, CaseCollector)
            else extract_case_collector(include)
            if include is not None
            else None
        )
        if sub is not None:
            config.storage.include(sub)


def extract_case_config(obj: object) -> t.Optional[CaseConfig[T]]:
    config = getattr(obj, "__pytest_case_config__", None)
    return config if isinstance(config, CaseConfig) else None


def extract_case_collector(obj: object) -> t.Optional[CaseCollector[T]]:
    config: t.Optional[CaseConfig[T]] = extract_case_config(obj)
    return config.storage if config is not None else None
