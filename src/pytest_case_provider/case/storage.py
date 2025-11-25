import abc
import inspect
import typing as t
from dataclasses import dataclass

from _pytest.mark import MarkDecorator
from _pytest.mark.structures import Mark, get_unpacked_marks
from typing_extensions import Concatenate, ParamSpec, Self, override

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc

U = ParamSpec("U")
T = t.TypeVar("T")
V = t.TypeVar("V")
S = t.TypeVar("S")


class CaseStorage(CaseCollector[T]):
    def __init__(self, cases: t.Optional[t.Sequence[CaseInfo[T]]] = None) -> None:
        self.__cases = list[CaseInfo[T]](cases or ())

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return iter(self.__cases)

    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        def inner(provider: CaseProviderFunc[U, T]) -> CaseProviderFunc[U, T]:
            self.append(provider, name=name, marks=marks)
            return provider

        return inner

    def append(
        self,
        provider: CaseProviderFunc[U, T],
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[t.Union[Mark, MarkDecorator]]] = None,
    ) -> Self:
        self.__cases.append(
            CaseInfo(
                name=name or provider.__name__,
                provider=CaseProvider(provider),
                marks=marks if marks is not None else get_unpacked_marks(provider),
            )
        )
        return self

    def extend(self, *stores: t.Union[t.Sequence[CaseInfo[T]], CaseCollector[T]]) -> Self:
        for store in stores:
            if isinstance(store, CaseCollector):
                self.__cases.extend(store.collect_cases())
            else:
                self.__cases.extend(case for case in store)

        return self


class CompositeCaseStorage(CaseCollector[T]):
    def __init__(self, *substores: CaseCollector[T]) -> None:
        self.__substores = list(substores)
        self.__inner = CaseStorage[T]()
        self.__substores.append(self.__inner)

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        known = set[CaseProvider[T]]()

        for store in self.__substores:
            for case in store.collect_cases():
                if case.provider not in known:
                    known.add(case.provider)
                    yield case

    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        return self.__inner.case(name=name, marks=marks)

    def append(
        self,
        provider: CaseProviderFunc[U, T],
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> Self:
        self.__inner.append(provider, name=name, marks=marks)
        return self

    def extend(self, *stores: t.Union[t.Sequence[CaseInfo[T]], CaseCollector[T]]) -> Self:
        self.__inner.extend(*stores)
        return self

    def include(self, *others: CaseCollector[T]) -> Self:
        self.__substores.extend(others)
        return self


@dataclass(frozen=True)
class CaseConfig(t.Generic[T]):
    storage: CompositeCaseStorage[T]
    case_parameter: inspect.Parameter


class CaseConfigHolder(t.Protocol[T]):
    __pytest_case_config__: CaseConfig[T]

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


class FuncCaseStorage(CaseConfigHolder[T], t.Protocol[T, U, V]):
    __call__: t.Callable[Concatenate[T, U], V]


class MethodCaseStorage(CaseConfigHolder[T], t.Protocol[S, T, U, V]):
    __call__: t.Callable[Concatenate[S, T, U], V]
