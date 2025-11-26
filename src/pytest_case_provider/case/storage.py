import itertools
import typing as t

from _pytest.mark import MarkDecorator
from _pytest.mark.structures import Mark, get_unpacked_marks
from typing_extensions import ParamSpec, Self, override

from pytest_case_provider.case.abc import CaseCollector, CaseStorage
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc

U = ParamSpec("U")
T = t.TypeVar("T")
V = t.TypeVar("V")
S = t.TypeVar("S")


class SimpleCaseStorage(CaseStorage[T]):
    def __init__(self, cases: t.Optional[t.Sequence[CaseInfo[T]]] = None) -> None:
        self.__cases = list[CaseInfo[T]](cases or ())

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return iter(self.__cases)

    @override
    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        def inner(provider: CaseProviderFunc[U, T]) -> CaseProviderFunc[U, T]:
            self.append(provider, name=name, marks=marks)
            return provider

        return inner

    @override
    def include(self, *others: CaseCollector[T]) -> Self:
        for store in others:
            self.__cases.extend(store.collect_cases())

        return self

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


class CompositeCaseStorage(CaseStorage[T]):
    def __init__(self, *substores: CaseCollector[T]) -> None:
        self.__substores = list(substores)
        self.__inner = SimpleCaseStorage[T]()
        self.__substores.append(self.__inner)

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return itertools.chain.from_iterable(store.collect_cases() for store in self.__substores)

    @override
    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        return self.__inner.case(name=name, marks=marks)

    @override
    def include(self, *others: CaseCollector[T]) -> Self:
        self.__substores.extend(others)
        return self
