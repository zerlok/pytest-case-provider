import typing as t
from dataclasses import dataclass

import nox


@dataclass(frozen=True)
class PytestMatrixItem:
    name: str
    python: t.Sequence[str]
    dependencies: t.Mapping[str, str]


# TODO: load supported versions from pyproject.toml
# TODO: support older python versions
# PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]
PYTHON_VERSIONS = ["3.12", "3.13", "3.14"]

PYTEST_MATRIX = [
    # TODO: support older pytest versions, note: pytest-asyncio < 1.0.0 must be used for older pytest; pytest-asyncio
    #  < 1.0.0 manages async fixtures differently, making it hard to invoke case providers properly.
    # PytestMatrixItem(
    #     name="v6",
    #     python=PYTHON_VERSIONS,
    #     dependencies={
    #         "pytest": "6.2.5",
    #         "pytest-asyncio": "0.20.3",
    #         "pytest-cov": "6.3.0",
    #     },
    # ),
    # PytestMatrixItem(
    #     name="v7",
    #     python=PYTHON_VERSIONS,
    #     dependencies={
    #         "pytest": "7.4.4",
    #         "pytest-asyncio": "0.23.8",
    #         "pytest-cov": "6.3.0",
    #     },
    # ),
    PytestMatrixItem(
        name="v8",
        python=PYTHON_VERSIONS,
        dependencies={
            "pytest": "8.4.2",
            "pytest-asyncio": "1.2.0",
            "pytest-cov": "7.0.0",
        },
    ),
]


@nox.session(name="ruff", python=PYTHON_VERSIONS, reuse_venv=True)
def run_ruff(session: nox.Session) -> None:
    session.run("poetry", "install", "--all-extras", external=True)
    session.run("poetry", "run", "ruff", "check", external=True)
    session.run("poetry", "run", "ruff", "format", "--check", external=True)


@nox.session(name="mypy", python=PYTHON_VERSIONS, reuse_venv=True)
def run_mypy(session: nox.Session) -> None:
    session.run("poetry", "install", "--all-extras", external=True)
    session.run("poetry", "run", "mypy", external=True)


@nox.session(name="pytest", python=PYTHON_VERSIONS, reuse_venv=True)
@nox.parametrize("matrix", PYTEST_MATRIX, ids=[item.name for item in PYTEST_MATRIX])
def run_pytest(session: nox.Session, matrix: PytestMatrixItem) -> None:
    if session.python not in matrix.python:
        session.skip("unsupported python version", session.python, matrix.name)

    session.install(*[f"{name}=={version}" for name, version in matrix.dependencies.items()])
    session.install("-e", ".")
    session.run("pytest", "--cov-report=xml", "--cov-append")
