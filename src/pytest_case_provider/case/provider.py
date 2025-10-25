import inspect
import typing as t
from contextlib import asynccontextmanager, contextmanager

from _pytest.fixtures import SubRequest

from pytest_case_provider.fixture import invoke_with_fixture_values

type CaseProviderFunc[**U, V] = t.Union[
    t.Callable[U, V],
    t.Callable[U, t.Iterator[V]],
    t.Callable[U, t.Coroutine[None, None, V]],
    t.Callable[U, t.AsyncIterator[V]],
]


class CaseProvider[V]:
    def __init__(self, func: CaseProviderFunc[..., V]) -> None:
        self.__func = func

    @property
    def is_async(self) -> bool:
        return inspect.iscoroutinefunction(self.__func) or inspect.isasyncgenfunction(self.__func)

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.__func)

    @contextmanager
    def provide_sync(self, request: SubRequest) -> t.Iterator[V]:
        if inspect.isgeneratorfunction(self.__func):
            for case in invoke_with_fixture_values(request, self.__func):
                yield case

        else:
            case = invoke_with_fixture_values(request, self.__func)
            yield t.cast("V", case)

    @asynccontextmanager
    async def provide_async(self, request: SubRequest) -> t.AsyncIterator[V]:
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
            yield t.cast("V", case)
