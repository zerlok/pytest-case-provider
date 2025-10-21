import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from _pytest.pytester import Pytester, RunResult

pytest_plugins = "pytester"


@dataclass()
class Report:
    passed: set[str] = field(default_factory=set)
    skipped: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    error: set[str] = field(default_factory=set)
    xfail: set[str] = field(default_factory=set)
    xpass: set[str] = field(default_factory=set)


TEST_RESULT_PATTERN = re.compile(
    r"^(?P<name>[\w./:\[\]-]+)\s+(?P<status>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\s*(?:\[\s*\d+%\])?$"
)


def parse_report(result: RunResult) -> Report:
    report = Report()
    status2collection = {
        "PASSED": report.passed,
        "SKIPPED": report.skipped,
        "FAILED": report.failed,
        "ERROR": report.error,
        "XFAIL": report.xfail,
        "XPASS": report.xpass,
    }

    for line in result.outlines:
        match = TEST_RESULT_PATTERN.search(line)
        if match is not None:
            status = match.group("status")
            status2collection[status].add(match.group("name"))

    return report


@pytest.mark.parametrize(
    ("path", "report"),
    [
        pytest.param(
            (Path(__file__).parent / "inject_case.py"),
            Report(
                passed={
                    "test_inject_case_parametrizes_test_functions.py::TestClass::test_class_simple[case_class_number]",
                    "test_inject_case_parametrizes_test_functions.py::TestClass::test_class_simple[case_four]",
                    "test_inject_case_parametrizes_test_functions.py::TestClass::test_class_simple[case_three]",
                    "test_inject_case_parametrizes_test_functions.py::TestClass::test_without_case_injection",
                    "test_inject_case_parametrizes_test_functions.py::test_case_injected[case_number]",
                    "test_inject_case_parametrizes_test_functions.py::test_case_injected[case_one]",
                    "test_inject_case_parametrizes_test_functions.py::test_case_injected[case_two]",
                    "test_inject_case_parametrizes_test_functions.py::test_without_case_injection",
                },
                skipped={
                    "test_inject_case_parametrizes_test_functions.py::TestClass::test_no_case_injected[NOTSET]",
                    "test_inject_case_parametrizes_test_functions.py::test_no_case_injected[NOTSET]",
                },
            ),
        )
    ],
)
def test_inject_case_parametrizes_test_functions(pytester: Pytester, path: Path, report: Report) -> None:
    pytester.makepyfile(path.read_text())
    result = pytester.runpytest("-vvv")

    assert parse_report(result) == report
