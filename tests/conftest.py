import importlib
import shutil
import typing as t
from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest
from _pytest.pytester import Pytester

_ANYIO_BACKENDS = ["asyncio"]


@pytest.fixture(scope="module", params=_ANYIO_BACKENDS)
def anyio_backend(request: SubRequest) -> str:
    return request.param


@pytest.fixture(scope="module")
def async_mode_ini_options() -> t.Optional[str]:
    plugin_pytest_run_args = {
        "anyio": 'anyio_mode = "auto"',
        "pytest_asyncio": 'asyncio_mode = "auto"',
    }

    for plugin, args in plugin_pytest_run_args.items():
        try:
            importlib.import_module(plugin)
        except ImportError:  # noqa: PERF203
            continue
        else:
            return args

    msg = "async mode is undefined"
    raise RuntimeError(msg)


@pytest.fixture
def pytester(pytester: Pytester, async_mode_ini_options: t.Optional[str]) -> Pytester:
    # NOTE: fixes run via nox
    sandbox_path = pytester.path / "tests"
    sandbox_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path(__file__).parent / "stub", sandbox_path / "stub")

    if async_mode_ini_options is not None:
        pytester.makeini(f"""
[tool.pytest.ini_options]
{async_mode_ini_options}
""")

    return pytester
