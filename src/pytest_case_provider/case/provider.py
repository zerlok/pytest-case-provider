import inspect
import typing as t
from contextlib import asynccontextmanager, contextmanager

from _pytest.fixtures import SubRequest
from typing_extensions import ParamSpec, override

from pytest_case_provider.fixture import invoke_with_fixture_values

U = ParamSpec("U")
V_co = t.TypeVar("V_co", covariant=True)
T = t.TypeVar("T")


class CaseProviderFunc(t.Protocol[U, T]):
    __name__: str
    __call__: t.Union[
        t.Callable[U, T],
        t.Callable[U, t.Iterator[T]],
        t.Callable[U, t.Coroutine[None, None, T]],
        t.Callable[U, t.AsyncIterator[T]],
    ]


class CaseProvider(t.Generic[V_co]):
    def __init__(self, func: CaseProviderFunc[t.Any, V_co]) -> None:
        self.__func = func

    @override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.__func}>"

    @property
    def is_async(self) -> bool:
        return inspect.iscoroutinefunction(self.__func) or inspect.isasyncgenfunction(self.__func)

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.__func)

    @contextmanager
    def provide_sync(self, request: SubRequest) -> t.Iterator[V_co]:
        if inspect.isgeneratorfunction(self.__func):
            for case in invoke_with_fixture_values(request, self.__func):
                yield case

        else:
            case = invoke_with_fixture_values(request, self.__func)
            yield t.cast("V_co", case)

    @asynccontextmanager
    async def provide_async(self, request: SubRequest) -> t.AsyncIterator[V_co]:
        if inspect.isasyncgenfunction(self.__func):
            async for case in invoke_with_fixture_values(request, self.__func):
                yield case

        elif inspect.iscoroutinefunction(self.__func):
            case = await invoke_with_fixture_values(request, self.__func)
            yield case

        elif inspect.isgeneratorfunction(self.__func):
            for case in invoke_with_fixture_values(request, self.__func):
                yield case

        else:
            case = invoke_with_fixture_values(request, self.__func)
            yield t.cast("V_co", case)
