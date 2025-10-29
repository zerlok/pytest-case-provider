from functools import cache

from _pytest.python import Metafunc

from pytest_case_provider.case.generator import CaseParametrizedTestGenerator


def pytest_generate_tests(metafunc: Metafunc) -> None:
    _get_case_test_generator().generate(metafunc)


@cache
def _get_case_test_generator() -> CaseParametrizedTestGenerator:
    return CaseParametrizedTestGenerator()
