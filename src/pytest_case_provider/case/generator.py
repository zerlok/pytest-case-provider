import typing as t

from _pytest.fixtures import SubRequest
from _pytest.mark import ParameterSet
from _pytest.python import Metafunc

from pytest_case_provider.case.decorator import extract_case_config
from pytest_case_provider.case.provider import CaseProvider
from pytest_case_provider.fixture import parametrize_metafunc_with_fixture_params

if t.TYPE_CHECKING:
    from pytest_case_provider.case.storage import CaseConfig


class CaseParametrizedTestGenerator:
    """Generates test functions for each case accordingly using pytest's parametrize feature."""

    # TODO: consider case injection into pytest fixtures directly.
    def generate(self, metafunc: Metafunc) -> None:
        config: t.Optional[CaseConfig[object]] = extract_case_config(metafunc.function)

        if config is not None:
            # TODO: deduplicate cases
            cases = list(config.storage.collect_cases())
            is_async = any(case.provider.is_async for case in cases)

            parametrize_metafunc_with_fixture_params(
                metafunc=metafunc,
                name=config.case_parameter.name,
                fixture_func=_invoke_provider_async if is_async else _invoke_provider,
                params=[
                    ParameterSet.param(
                        case.provider,
                        id=case.name,
                        marks=case.marks,
                    )
                    for case in cases
                ],
            )


async def _invoke_provider_async(request: SubRequest) -> t.AsyncIterator[object]:
    provider = request.param
    # NOTE: test generator parametrizes this fixture, thus this check should always pass
    assert isinstance(provider, CaseProvider), f"CaseProvider type was expected, got: {provider}"

    async with provider.provide_async(request) as case:
        yield case


def _invoke_provider(request: SubRequest) -> t.Iterator[object]:
    provider = request.param
    # NOTE: test generator parametrizes this fixture, thus this check should always pass
    assert isinstance(provider, CaseProvider), f"CaseProvider type was expected, got: {provider}"

    with provider.provide_sync(request) as case:
        yield case
