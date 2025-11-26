import abc
import typing as t

from _pytest.mark import MarkDecorator
from typing_extensions import Concatenate, ParamSpec, Self

from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProviderFunc

V_co = t.TypeVar("V_co", covariant=True)
U = ParamSpec("U")
T = t.TypeVar("T")
V = t.TypeVar("V")
S = t.TypeVar("S")


class CaseCollector(t.Generic[V_co], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def collect_cases(self) -> t.Iterable[CaseInfo[V_co]]:
        raise NotImplementedError


class CaseRegistry(t.Protocol[T]):
    @abc.abstractmethod
    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        raise NotImplementedError

    @abc.abstractmethod
    def include(self, *others: CaseCollector[T]) -> Self:
        raise NotImplementedError


class CaseStorage(CaseCollector[T], CaseRegistry[T], t.Generic[T], metaclass=abc.ABCMeta):
    pass


class FuncCaseRegistry(CaseRegistry[T], t.Protocol[T, U, V]):
    __call__: t.Callable[Concatenate[T, U], V]


class MethodCaseRegistry(CaseRegistry[T], t.Protocol[S, T, U, V]):
    __call__: t.Callable[Concatenate[S, T, U], V]
