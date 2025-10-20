import typing as t

from _pytest.fixtures import SubRequest
from _pytest.mark import ParameterSet
from _pytest.python import Metafunc

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.provider import CaseProvider
from pytest_case_provider.fixture import parametrize_metafunc_with_fixture_params


class CaseFixtureTestGenerator:
    def generate(self, metafunc: Metafunc) -> None:
        func = metafunc.function

        if isinstance(func, CaseCollector):
            cases = list(func.collect_cases())
            case_param = func.get_case_param()

            fixture_func = self.__build_fixture_func(
                is_async=any(case.provider.is_async for case in cases),
                of_type=case_param.annotation,
            )

            parametrize_metafunc_with_fixture_params(
                metafunc=metafunc,
                name=case_param.name,
                fixture_func=fixture_func,
                params=[
                    ParameterSet.param(
                        case.provider,
                        id=case.name,
                        marks=case.marks,
                    )
                    for case in cases
                ],
            )

    def __build_fixture_func(
        self,
        is_async: bool,
        of_type: t.Optional[type[object]] = None,
    ) -> t.Callable[..., object]:
        if is_async:

            async def invoke_async(request: SubRequest) -> t.AsyncIterator[object]:
                provider = request.param
                if not isinstance(provider, CaseProvider):
                    msg = "CaseProvider type was expected"
                    raise TypeError(msg, provider)

                async with provider.provide_async(request) as case:
                    assert of_type is None or isinstance(case, of_type)
                    yield case

            return invoke_async

        else:

            def invoke(request: SubRequest) -> t.Iterator[object]:
                provider = request.param
                if not isinstance(provider, CaseProvider):
                    msg = "CaseProvider type was expected"
                    raise TypeError(msg, provider)

                with provider.provide_sync(request) as case:
                    assert of_type is None or isinstance(case, of_type)
                    yield case

            return invoke
