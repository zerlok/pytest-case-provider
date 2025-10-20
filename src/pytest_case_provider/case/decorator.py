import inspect
import typing as t
from functools import wraps

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
    def get_signature(self) -> inspect.Signature:
        return inspect.signature(self.__testfunc)

    @t.override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return self.__cases

    def case[**S](
        self,
        name: t.Optional[str] = None,
    ) -> t.Callable[[CaseProviderFunc[S, T]], CaseProviderFunc[S, T]]:
        return self.__cases.case(name=name)

    def include(self, *others: CaseStorage[T]) -> t.Self:
        self.__cases.extend(*others)
        return self


def inject_cases[**U, V, T](
    testfunc: t.Callable[t.Concatenate[T, U], V],
) -> TestFuncCaseDecorator[U, V, T]:
    wrapped = wraps(testfunc)(TestFuncCaseDecorator(testfunc, CaseStorage[T]()))
    return t.cast("TestFuncCaseDecorator[U, V, T]", wrapped)
