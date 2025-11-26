import typing as t

import pytest
from _pytest.fixtures import SubRequest
from _pytest.pytester import Pytester


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("pytest_asyncio", 'asyncio_mode = "auto"'), id="pytest-asyncio"),
    ],
)
def async_mode_ini_options(request: SubRequest) -> t.Optional[str]:
    modulename, options = request.param
    pytest.importorskip(modulename)
    return options


@pytest.fixture
def pytester(pytester: Pytester, async_mode_ini_options: t.Optional[str]) -> Pytester:
    if async_mode_ini_options is not None:
        pytester.makepyprojecttoml(f"""
[tool.pytest.ini_options]
{async_mode_ini_options}
""")

    return pytester
