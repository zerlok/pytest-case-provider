import importlib
import inspect
import typing as t
from types import ModuleType

from _pytest.fixtures import SubRequest
from _pytest.mark import ParameterSet
from _pytest.python import Metafunc

from pytest_case_provider.case import InspectingCaseCollector
from pytest_case_provider.case.abc import CaseCollector, CaseRegistry, CaseStorage
from pytest_case_provider.case.configure import extract_case_parameter, extract_case_storage
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider
from pytest_case_provider.fixture import parametrize_metafunc_with_fixture_params

T = t.TypeVar("T")


class CaseParametrizedTestGenerator:
    """Generates test functions for each case accordingly using pytest's parametrize feature."""

    # TODO: consider case injection into pytest fixtures directly.
    def generate(self, metafunc: Metafunc) -> None:
        case_storage: t.Optional[CaseStorage[object]] = extract_case_storage(metafunc.function)
        case_parameter: t.Optional[inspect.Parameter] = extract_case_parameter(metafunc.function)

        if case_storage is not None and case_parameter is not None:
            case_module = self._load_test_cases_module(metafunc.module)
            if case_module is not None:
                self._include_module_cases(case_storage, case_module, case_parameter)

            cases = list(self._collect_cases(case_storage))
            is_async = any(case.provider.is_async for case in cases)

            parametrize_metafunc_with_fixture_params(
                metafunc=metafunc,
                name=case_parameter.name,
                fixture_func=_invoke_provider_async if is_async else _invoke_provider,
                params=self._build_fixture_params(cases),
            )

    def _load_test_cases_module(
        self,
        module: ModuleType,
    ) -> t.Optional[ModuleType]:
        package, _, name = module.__name__.rpartition(".")
        if not name:
            return None

        case_prefix = getattr(module, "case_prefix", "case_")
        if not isinstance(case_prefix, str):
            return None

        base_name = name.removeprefix("test_")
        if not base_name:
            return None

        case_module_name = f"{case_prefix}{base_name}"
        qualname = f"{package}.{case_module_name}" if package else case_module_name
        try:
            return importlib.import_module(qualname)

        except ImportError:
            return None

    def _include_module_cases(
        self,
        registry: CaseRegistry[T],
        module: ModuleType,
        parameter: inspect.Parameter,
    ) -> None:
        registry.include(InspectingCaseCollector(module, parameter.annotation))

    def _collect_cases(self, collector: CaseCollector[T]) -> t.Iterable[CaseInfo[T]]:
        known = set[str]()

        for case in collector.collect_cases():
            if case.name not in known:
                known.add(case.name)
                yield case

    def _build_fixture_params(self, cases: t.Sequence[CaseInfo[T]]) -> t.Sequence[ParameterSet]:
        return [
            ParameterSet.param(
                case.provider,
                id=case.name,
                marks=case.marks,
            )
            for case in cases
        ]


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
