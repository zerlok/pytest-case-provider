import typing as t
from itertools import chain

from _pytest.mark import MarkDecorator

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc


class CaseStorage[T](CaseCollector[T]):
    def __init__(self, cases: t.Sequence[CaseInfo[T]] | None = None) -> None:
        self.__cases = list[CaseInfo[T]](cases or ())

    @t.override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return iter(self.__cases)

    def case[**U](
        self,
        name: str | None = None,
        marks: t.Sequence[MarkDecorator] | None = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        def inner(provider: CaseProviderFunc[U, T]) -> CaseProviderFunc[U, T]:
            self.append(provider, name=name, marks=marks)
            return provider

        return inner

    def append[**U](
        self,
        provider: CaseProviderFunc[U, T],
        name: str | None = None,
        marks: t.Sequence[MarkDecorator] | None = None,
    ) -> t.Self:
        self.__cases.append(
            CaseInfo(
                name=name or provider.__name__,
                provider=CaseProvider(provider),
                marks=marks or (),
            )
        )
        return self

    def extend(self, *stores: t.Union[t.Sequence[CaseInfo[T]], CaseCollector[T]]) -> t.Self:
        for store in stores:
            if isinstance(store, CaseCollector):
                self.__cases.extend(store.collect_cases())
            else:
                self.__cases.extend(case for case in store)

        return self


class CompositeCaseStorage[T](CaseCollector[T]):
    def __init__(self, *stores: CaseCollector[T]) -> None:
        self.__substores = list(stores)
        self.__inner = CaseStorage[T]()
        self.__substores.append(self.__inner)

    @t.override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return chain.from_iterable(store.collect_cases() for store in self.__substores)

    def case[**U](
        self,
        name: str | None = None,
        marks: t.Sequence[MarkDecorator] | None = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        return self.__inner.case(name=name, marks=marks)

    def append[**U](
        self,
        provider: CaseProviderFunc[U, T],
        name: str | None = None,
        marks: t.Sequence[MarkDecorator] | None = None,
    ) -> t.Self:
        self.__inner.append(provider, name=name, marks=marks)
        return self

    def extend(self, *stores: t.Union[t.Sequence[CaseInfo[T]], CaseCollector[T]]) -> t.Self:
        for store in stores:
            if isinstance(store, CaseCollector):
                self.__substores.append(store)
            else:
                self.__inner.extend(store)

        return self

    def include(self, *others: CaseCollector[T]) -> t.Self:
        self.__substores.extend(others)
        return self
