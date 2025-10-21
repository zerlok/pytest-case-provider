import inspect
import typing as t
from functools import partial, wraps

from _pytest.mark import MarkDecorator

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProviderFunc
from pytest_case_provider.case.storage import CaseStorage


class TestFuncCaseDecorator[**U, V, T](CaseCollector):
    def __init__(
        self,
        testfunc: t.Callable[U, V],
        cases: CaseStorage[T],
    ) -> None:
        self.__testfunc = testfunc
        self.__cases = cases

    @t.override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testfunc}>"

    def __call__(self, *args: U.args, **kwargs: U.kwargs) -> V:
        return self.__testfunc(*args, **kwargs)

    @t.override
    def get_case_param(self) -> inspect.Parameter:
        return next(iter(inspect.signature(self.__testfunc).parameters.values()))

    @t.override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return self.__cases

    def case[**X](
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[X, T]], CaseProviderFunc[X, T]]:
        return self.__cases.case(name=name, marks=marks)

    def include(self, *others: CaseStorage[T]) -> t.Self:
        self.__cases.extend(*others)
        return self


class TestMethodCaseDecorator[**U, V, T, S](CaseCollector):
    def __init__(
        self,
        testmethod: t.Callable[t.Concatenate[S, T, U], V],
        cases: CaseStorage[T],
    ) -> None:
        self.__testmethod = testmethod
        self.__cases = cases

    @t.override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testmethod}>"

    @t.overload
    def __get__(self, instance: None, owner: type[S]) -> t.Self: ...

    @t.overload
    def __get__(self, instance: S, owner: type[S]) -> t.Callable[t.Concatenate[T, U], V]: ...

    def __get__(self, instance: t.Optional[S], owner: type[S]) -> t.Union[t.Self, t.Callable[t.Concatenate[T, U], V]]:
        return partial(self.__testmethod, instance) if instance is not None else self

    def __call__(self, instance: S, case: T, *args: U.args, **kwargs: U.kwargs) -> V:
        return self.__testmethod(instance, case, *args, **kwargs)

    @t.override
    def get_case_param(self) -> inspect.Parameter:
        params = iter(inspect.signature(self.__testmethod).parameters.values())
        # skip `self`
        _ = next(params)
        return next(params)

    @t.override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return self.__cases

    def case[**X](
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[X, T]], CaseProviderFunc[X, T]]:
        return self.__cases.case(name=name, marks=marks)

    def include(self, *others: CaseStorage[T]) -> t.Self:
        self.__cases.extend(*others)
        return self


def inject_cases[**U, V, T](
    testfunc: t.Callable[t.Concatenate[T, U], V],
) -> TestFuncCaseDecorator[U, V, T]:
    wrapped = wraps(testfunc)(TestFuncCaseDecorator(testfunc, CaseStorage[T]()))
    return t.cast("TestFuncCaseDecorator[U, V, T]", wrapped)


def inject_cases_method[**U, V, T, S](
    testmethod: t.Callable[t.Concatenate[S, T, U], V],
) -> TestMethodCaseDecorator[U, V, T, S]:
    wrapped = wraps(testmethod)(TestMethodCaseDecorator(testmethod, CaseStorage[T]()))
    return t.cast("TestMethodCaseDecorator[U, V, T, S]", wrapped)
