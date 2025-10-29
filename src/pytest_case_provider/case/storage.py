import typing as t
from itertools import chain

from _pytest.mark import MarkDecorator
from _pytest.mark.structures import Mark, get_unpacked_marks
from typing_extensions import ParamSpec, Self, override

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc

U = ParamSpec("U")
V_co = t.TypeVar("V_co", covariant=True)


class CaseStorage(CaseCollector[V_co]):
    def __init__(self, cases: t.Optional[t.Sequence[CaseInfo[V_co]]] = None) -> None:
        self.__cases = list[CaseInfo[V_co]](cases or ())

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[V_co]]:
        return iter(self.__cases)

    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, V_co]], CaseProviderFunc[U, V_co]]:
        def inner(provider: CaseProviderFunc[U, V_co]) -> CaseProviderFunc[U, V_co]:
            self.append(provider, name=name, marks=marks)
            return provider

        return inner

    def append(
        self,
        provider: CaseProviderFunc[U, V_co],
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

    def extend(self, *stores: t.Union[t.Sequence[CaseInfo[V_co]], CaseCollector[V_co]]) -> Self:
        for store in stores:
            if isinstance(store, CaseCollector):
                self.__cases.extend(store.collect_cases())
            else:
                self.__cases.extend(case for case in store)

        return self


class CompositeCaseStorage(CaseCollector[V_co]):
    def __init__(self, *substores: CaseCollector[V_co]) -> None:
        self.__substores = list(substores)
        self.__inner = CaseStorage[V_co]()
        self.__substores.append(self.__inner)

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[V_co]]:
        return chain.from_iterable(store.collect_cases() for store in self.__substores)

    def case(
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, V_co]], CaseProviderFunc[U, V_co]]:
        return self.__inner.case(name=name, marks=marks)

    def append(
        self,
        provider: CaseProviderFunc[U, V_co],
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> Self:
        self.__inner.append(provider, name=name, marks=marks)
        return self

    def extend(self, *stores: t.Union[t.Sequence[CaseInfo[V_co]], CaseCollector[V_co]]) -> Self:
        self.__inner.extend(*stores)
        return self

    def include(self, *others: CaseCollector[V_co]) -> Self:
        self.__substores.extend(others)
        return self
