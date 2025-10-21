import typing as t

from _pytest.mark import MarkDecorator

from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc


class CaseStorage[T](t.Sequence[CaseInfo[T]]):
    def __init__(self, params: t.Optional[t.Sequence[CaseInfo[T]]] = None) -> None:
        self.__cases = list[CaseInfo[T]](params or ())

    @t.overload
    def __getitem__(self, index: int) -> CaseInfo[T]: ...

    @t.overload
    def __getitem__(self, index: slice) -> t.Sequence[CaseInfo[T]]: ...

    @t.override
    def __getitem__(
        self,
        index: t.Union[int, slice],
    ) -> t.Union[CaseInfo[T], t.Sequence[CaseInfo[T]]]:
        return self.__cases.__getitem__(index)

    @t.override
    def __len__(self) -> int:
        return len(self.__cases)

    def case[**U](
        self,
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Callable[[CaseProviderFunc[U, T]], CaseProviderFunc[U, T]]:
        def inner(provider: CaseProviderFunc[U, T]) -> CaseProviderFunc[U, T]:
            self.append(provider, name=name, marks=marks)
            return provider

        return inner

    def append[**U](
        self,
        provider: CaseProviderFunc[U, T],
        name: t.Optional[str] = None,
        marks: t.Optional[t.Sequence[MarkDecorator]] = None,
    ) -> t.Self:
        self.__cases.append(
            CaseInfo(
                name=name or provider.__name__,
                provider=CaseProvider(provider),
                marks=marks or (),
            )
        )
        return self

    def extend(self, *stores: t.Iterable[CaseInfo[T]]) -> t.Self:
        self.__cases.extend(case for store in stores for case in store)
        return self

    def union(self, *stores: t.Iterable[CaseInfo[T]]) -> t.Self:
        clone = self.__class__()
        return clone.extend(self, *stores)
