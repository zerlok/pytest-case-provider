import inspect
import typing as t
from functools import WRAPPER_ASSIGNMENTS, partial, update_wrapper, wraps

from _pytest.mark import MarkDecorator
from typing_extensions import Concatenate, ParamSpec, Self, override

from pytest_case_provider.abc import CaseCollector, CaseParametrizer
from pytest_case_provider.case.storage import CompositeCaseStorage

U = ParamSpec("U")
F = t.TypeVar("F")
V_co = t.TypeVar("V_co", covariant=True)
T_co = t.TypeVar("T_co", covariant=True)
S_contra = t.TypeVar("S_contra", contravariant=True)


# NOTE: `__globals__` is used by pytest marks such as `pytest.mark.skipif` to evaluate string condition.
_TEST_FUNC_WRAPPER_ASSIGNMENT: t.Final[t.Sequence[str]] = [*WRAPPER_ASSIGNMENTS, "__globals__"]


class FuncDecorator:
    def __init__(
        self,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> None:
        self.__marks = marks

    def apply(self, func: F) -> F:
        for mark in self.__marks or ():
            func = t.cast("F", mark(func))

        return func


class FuncCaseStorage(CompositeCaseStorage[T_co], CaseParametrizer[T_co], t.Generic[U, V_co, T_co]):
    """
    Stores cases of a specific type `T_co` for a specific test function.

    Instances of this class are intended to be collected by pytest to generate test for each case.

    During pytest test run this object delegates the call to actual test function.
    """

    def __init__(self, testfunc: t.Callable[Concatenate[T_co, U], V_co]) -> None:
        super().__init__()
        self.__testfunc = testfunc
        update_wrapper(self, self.__testfunc, assigned=_TEST_FUNC_WRAPPER_ASSIGNMENT)

    @override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testfunc}>"

    def __call__(self, *args: U.args, **kwargs: U.kwargs) -> V_co:
        # NOTE: `T` should be provided in `kwargs` by pytest fixture injection
        return self.__testfunc(*args, **kwargs)  # type: ignore[arg-type]

    @override
    def get_case_param(self) -> inspect.Parameter:
        return next(iter(inspect.signature(self.__testfunc).parameters.values()))


class MethodCaseStorage(CompositeCaseStorage[T_co], CaseParametrizer[T_co], t.Generic[U, V_co, T_co, S_contra]):
    """
    Stores cases of a specific type `T_co` for a specific test method.

    Instances of this class are intended to be collected by pytest to generate test for each case.

    During pytest test run this object delegates the call to actual test method.
    """

    def __init__(self, testmethod: t.Callable[Concatenate[S_contra, T_co, U], V_co]) -> None:
        super().__init__()
        self.__testmethod = testmethod
        update_wrapper(self, self.__testmethod)

    @override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testmethod}>"

    @t.overload
    def __get__(self, instance: None, owner: type[S_contra]) -> Self: ...

    @t.overload
    def __get__(self, instance: S_contra, owner: type[S_contra]) -> t.Callable[Concatenate[T_co, U], V_co]: ...

    def __get__(
        self,
        instance: t.Optional[S_contra],
        owner: type[S_contra],
    ) -> t.Union[Self, t.Callable[Concatenate[T_co, U], V_co]]:
        return (
            wraps(self.__testmethod, assigned=_TEST_FUNC_WRAPPER_ASSIGNMENT)(partial(self, instance))
            if instance is not None
            else self
        )

    def __call__(self, instance: S_contra, *args: U.args, **kwargs: U.kwargs) -> V_co:
        # NOTE: `T` should be provided in `kwargs` by pytest fixture injection
        return self.__testmethod(instance, *args, **kwargs)  # type: ignore[arg-type]

    @override
    def get_case_param(self) -> inspect.Parameter:
        params = iter(inspect.signature(self.__testmethod).parameters.values())
        _ = next(params)  # skip `self`
        return next(params)


class FuncCaseStorageProvider(t.Generic[T_co]):
    """Provides `FuncCaseStorage` objects of a specific `T_co` case type."""

    def __init__(
        self,
        decorators: FuncDecorator,
        includes: t.Sequence[CaseCollector[T_co]],
    ) -> None:
        self.__decorators = decorators
        self.__includes = list(includes)

    def __call__(self, testfunc: t.Callable[Concatenate[T_co, U], V_co]) -> FuncCaseStorage[U, V_co, T_co]:
        storage = FuncCaseStorage[U, V_co, T_co](self.__decorators.apply(testfunc))
        storage.include(*self.__includes)
        return storage


class MethodCaseStorageProvider(t.Generic[T_co]):
    """Provides `MethodCaseStorage` objects of a specific `T_co` case type."""

    def __init__(
        self,
        decorators: FuncDecorator,
        includes: t.Sequence[CaseCollector[T_co]],
    ) -> None:
        self.__decorators = decorators
        self.__includes = list(includes)

    def __call__(
        self,
        testmethod: t.Callable[Concatenate[S_contra, T_co, U], V_co],
    ) -> MethodCaseStorage[U, V_co, T_co, S_contra]:
        storage = MethodCaseStorage[U, V_co, T_co, S_contra](self.__decorators.apply(testmethod))
        storage.include(*self.__includes)
        return storage


class FuncCaseStorageProviderPlaceholder:
    """A helper to infer `FuncCaseStorageProvider` type vars when test function is wrapped with python `@` syntax."""

    def __init__(self, decorators: FuncDecorator) -> None:
        self.__decorators = decorators

    def __call__(self, testfunc: t.Callable[Concatenate[T_co, U], V_co]) -> FuncCaseStorage[U, V_co, T_co]:
        return self.include()(testfunc)

    def include(self, *others: CaseCollector[T_co]) -> FuncCaseStorageProvider[T_co]:
        return FuncCaseStorageProvider(
            decorators=self.__decorators,
            includes=others,
        )


class MethodCaseStorageProviderPlaceholder:
    """A helper to infer `MethodCaseStorageProvider` type vars when test function is wrapped with python `@` syntax."""

    def __init__(self, decorators: FuncDecorator) -> None:
        self.__decorators = decorators

    def __call__(
        self,
        testmethod: t.Callable[Concatenate[S_contra, T_co, U], V_co],
    ) -> MethodCaseStorage[U, V_co, T_co, S_contra]:
        return self.include()(testmethod)

    def include(self, *others: CaseCollector[T_co]) -> MethodCaseStorageProvider[T_co]:
        return MethodCaseStorageProvider(decorators=self.__decorators, includes=others)


def inject_cases_func(
    marks: t.Optional[t.Sequence[MarkDecorator]] = None,
) -> FuncCaseStorageProviderPlaceholder:
    """
    Setup case provider injection into the test function.

    :param marks: list of pytest marks to apply on test function (useful when marks are not well annotated for MyPy).
    :return: a placeholder object that can wrap the test function.
    """
    return FuncCaseStorageProviderPlaceholder(FuncDecorator(marks))


def inject_cases_method(
    marks: t.Optional[t.Sequence[MarkDecorator]] = None,
) -> MethodCaseStorageProviderPlaceholder:
    """
    Setup case provider injection into the test method.

    :param marks: list of pytest marks to apply on test method (useful when marks are not well annotated for MyPy).
    :return: a placeholder object that can wrap the test method.
    """
    return MethodCaseStorageProviderPlaceholder(FuncDecorator(marks))
