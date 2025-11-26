import typing as t
from functools import partial

from _pytest.mark import MarkDecorator
from typing_extensions import Concatenate, ParamSpec, Self, override

from pytest_case_provider.case.abc import CaseCollector, CaseStorage, FuncCaseRegistry, MethodCaseRegistry
from pytest_case_provider.case.configure import configure_testfunc_cases, configure_testmethod_cases
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProviderFunc
from pytest_case_provider.case.storage import CompositeCaseStorage

S = t.TypeVar("S")
T = t.TypeVar("T")
U = ParamSpec("U")
V = t.TypeVar("V")


class CaseContainer(CaseStorage[T], t.Generic[T]):
    """
    Stores and injects cases into test functions & test methods.

    The same container instance injects cases with same storage instance across all injections.
    """

    def __init__(self, storage: t.Optional[CaseStorage[T]] = None) -> None:
        self.__storage = storage if storage is not None else CompositeCaseStorage[T]()

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return self.__storage.collect_cases()

    @override
    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        return self.__storage.case(name=name, marks=marks)

    @override
    def include(self, *others: CaseCollector[T]) -> Self:
        self.__storage.include(*others)
        return self

    def inject_func(self) -> t.Callable[[t.Callable[Concatenate[T, U], V]], FuncCaseRegistry[T, U, V]]:
        return partial(configure_testfunc_cases, storage=self.__storage)

    def inject_method(self) -> t.Callable[[t.Callable[Concatenate[S, T, U], V]], MethodCaseRegistry[S, T, U, V]]:
        return partial(configure_testmethod_cases, storage=self.__storage)
