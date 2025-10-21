import inspect
import typing as t
from functools import partial, update_wrapper, wraps

from pytest_case_provider.abc import CaseCollector, CaseParametrizer
from pytest_case_provider.case.storage import CompositeCaseStorage


class TestFuncCaseDecorator[**U, V, T](CompositeCaseStorage[T], CaseParametrizer[T]):
    def __init__(self, testfunc: t.Callable[t.Concatenate[T, U], V]) -> None:
        super().__init__()
        self.__testfunc = testfunc
        update_wrapper(self, self.__testfunc)

    @t.override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testfunc}>"

    def __call__(self, *args: U.args, **kwargs: U.kwargs) -> V:
        # NOTE: `T` should be provided in `kwargs` by pytest fixture injection
        return self.__testfunc(*args, **kwargs)  # type: ignore[arg-type]

    @t.override
    def get_case_param(self) -> inspect.Parameter:
        return next(iter(inspect.signature(self.__testfunc).parameters.values()))


class TestMethodCaseDecorator[**U, V, T, S](CompositeCaseStorage[T], CaseParametrizer[T]):
    def __init__(self, testmethod: t.Callable[t.Concatenate[S, T, U], V]) -> None:
        super().__init__()
        self.__testmethod = testmethod
        update_wrapper(self, self.__testmethod)

    @t.override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testmethod}>"

    @t.overload
    def __get__(self, instance: None, owner: type[S]) -> t.Self: ...

    @t.overload
    def __get__(self, instance: S, owner: type[S]) -> t.Callable[t.Concatenate[T, U], V]: ...

    def __get__(self, instance: S | None, owner: type[S]) -> t.Union[t.Self, t.Callable[t.Concatenate[T, U], V]]:
        return wraps(self.__testmethod)(partial(self, instance)) if instance is not None else self

    def __call__(self, instance: S, *args: U.args, **kwargs: U.kwargs) -> V:
        # NOTE: `T` should be provided in `kwargs` by pytest fixture injection
        return self.__testmethod(instance, *args, **kwargs)  # type: ignore[arg-type]

    @t.override
    def get_case_param(self) -> inspect.Parameter:
        params = iter(inspect.signature(self.__testmethod).parameters.values())
        _ = next(params)  # skip `self`
        return next(params)


class TestFuncCaseInjector[T]:
    def __init__(self, includes: t.Sequence[CaseCollector[T]]) -> None:
        self.__includes = includes

    def __call__[**U, V](self, testfunc: t.Callable[t.Concatenate[T, U], V]) -> TestFuncCaseDecorator[U, V, T]:
        collector = TestFuncCaseDecorator[U, V, T](testfunc)
        collector.include(*self.__includes)
        return collector


class TestMethodCaseInjector[T]:
    def __init__(self, includes: t.Sequence[CaseCollector[T]]) -> None:
        self.__includes = includes

    def __call__[**U, V, S](
        self,
        testmethod: t.Callable[t.Concatenate[S, T, U], V],
    ) -> TestMethodCaseDecorator[U, V, T, S]:
        collector = TestMethodCaseDecorator[U, V, T, S](testmethod)
        collector.include(*self.__includes)
        return collector


@t.overload
def inject_cases[**U, V, T](testfunc: t.Callable[t.Concatenate[T, U], V]) -> TestFuncCaseDecorator[U, V, T]: ...


@t.overload
def inject_cases[T](*includes: CaseCollector[T]) -> TestFuncCaseInjector[T]: ...


def inject_cases[**U, V, T](
    testfunc: t.Union[t.Callable[t.Concatenate[T, U], V] | None, CaseCollector[T]] = None,
    *includes: CaseCollector[T],
) -> t.Union[TestFuncCaseDecorator[U, V, T], TestFuncCaseInjector[T]]:
    if isinstance(testfunc, CaseCollector):
        return TestFuncCaseInjector((testfunc, *includes))

    else:
        injector = TestFuncCaseInjector(includes)
        return injector(testfunc) if testfunc is not None else injector


@t.overload
def inject_cases_method[**U, V, T, S](
    testmethod: t.Callable[t.Concatenate[S, T, U], V],
) -> TestMethodCaseDecorator[U, V, T, S]: ...


@t.overload
def inject_cases_method[T](*includes: CaseCollector[T]) -> TestMethodCaseInjector[T]: ...


def inject_cases_method[**U, V, T, S](
    testmethod: t.Union[t.Callable[t.Concatenate[S, T, U], V] | None, CaseCollector[T]] = None,
    *includes: CaseCollector[T],
) -> t.Union[TestMethodCaseDecorator[U, V, T, S], TestMethodCaseInjector[T]]:
    if isinstance(testmethod, CaseCollector):
        return TestMethodCaseInjector((testmethod, *includes))

    else:
        injector = TestMethodCaseInjector(includes)
        return injector(testmethod) if testmethod is not None else injector
