import inspect
import typing as t

import pytest
from _pytest.fixtures import SubRequest

from pytest_case_provider.model import CaseProviderFunc
from pytest_case_provider.parametrize import ParametrizedTestFunction

# def pytest_configure(config: pytest.Config) -> None:
#     config.addinivalue_line("markers", "case_provider: parametrization via case factories")


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    func = metafunc.function

    if isinstance(func, ParametrizedTestFunction):
        metafunc.parametrize(
            "provide_case",
            [
                pytest.param(
                    case.provider,
                    id=case.name,
                    marks=case.marks,
                )
                for case in func.collect_cases()
            ],
            indirect=True,
        )


@pytest.fixture
def provide_case[T](request: SubRequest) -> t.Iterator[T]:
    provider: CaseProviderFunc[t.Any, T] = request.param

    sig = inspect.signature(provider)
    kwargs = {p.name: request.getfixturevalue(p.name) for p in sig.parameters.values()}
    output = provider(**kwargs)

    if inspect.isgenerator(output):
        for case in output:
            yield case

    elif isinstance(output, t.ContextManager):
        with output as case:
            yield case

    else:
        yield output


@pytest.fixture
async def provide_case_async[T](request: SubRequest) -> t.AsyncIterator[T]:
    provider: CaseProviderFunc[t.Any, T] = request.param

    sig = inspect.signature(provider)
    kwargs = {p.name: request.getfixturevalue(p.name) for p in sig.parameters.values()}
    output = provider(**kwargs)

    if inspect.isasyncgen(output):
        async for case in output:
            yield case

    elif isinstance(output, t.AsyncContextManager):
        async with output as case:
            yield case

    elif inspect.isawaitable(output):
        case = await output
        yield case

    elif inspect.isgenerator(output):
        for case in output:
            yield case

    elif isinstance(output, t.ContextManager):
        with output as case:
            yield case

    else:
        yield output
