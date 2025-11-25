import shutil
import typing as t
from pathlib import Path

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
    # NOTE: fixes run via nox
    sandbox_path = pytester.path / "tests"
    sandbox_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path(__file__).parent / "stub", sandbox_path / "stub")

    if async_mode_ini_options is not None:
        pytester.makepyprojecttoml(f"""
[tool.pytest.ini_options]
{async_mode_ini_options}
""")

    return pytester
