import typing as t

import pytest
from _pytest.mark import ParameterSet


class CaseStorage[T](t.Iterable[ParameterSet]):
    def __init__(self, params: t.Optional[t.MutableSequence[ParameterSet]] = None) -> None:
        self.__params = params or []

    @t.override
    def __iter__(self) -> t.Iterator[ParameterSet]:
        return iter(self.__params)

    def case[**U](
        self,
        name: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable[U, T]], t.Callable[U, T]]:
        def inner(case_provider: t.Callable[U, T]) -> t.Callable[U, T]:
            self.append(case_provider, name=name)
            return case_provider

        return inner

    def append[**U](
        self,
        provider: t.Callable[U, T],
        name: t.Optional[str] = None,
    ) -> t.Self:
        param = pytest.param(
            provider,
            id=name or provider.__name__,
            # TODO: get marks from case provider func
            #  marks=None,
        )
        self.__params.append(param)

        return self

    def extend(self, *others: t.Iterable[ParameterSet]) -> t.Self:
        self.__params.extend(param for other in others for param in other)
        return self

    def union(self, *others: t.Iterable[ParameterSet]) -> t.Self:
        clone = self.__class__()
        return clone.extend(self, *others)
