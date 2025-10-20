from functools import cache

from _pytest.python import Metafunc

from pytest_case_provider.case.generator import CaseFixtureTestGenerator


def pytest_generate_tests(metafunc: Metafunc) -> None:
    _get_generator().generate(metafunc)


@cache
def _get_generator() -> CaseFixtureTestGenerator:
    return CaseFixtureTestGenerator()
