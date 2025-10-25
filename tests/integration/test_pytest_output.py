import re
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from _pytest.pytester import Pytester

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


def parse_report(outlines: t.Sequence[str]) -> Report:
    report = Report()
    status2collection = {
        "PASSED": report.passed,
        "SKIPPED": report.skipped,
        "FAILED": report.failed,
        "ERROR": report.error,
        "XFAIL": report.xfail,
        "XPASS": report.xpass,
    }

    for line in outlines:
        match = TEST_RESULT_PATTERN.match(line)
        if match is not None:
            status = match.group("status")
            status2collection[status].add(match.group("name"))

    return report


@pytest.mark.parametrize(
    ("path", "report"),
    [
        pytest.param(
            Path(__file__).parent / "test_inject_cases.py",
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
                    # injected cases from test_case_injected + one special case
                    "test_inject_case_parametrizes_test_functions.py::test_case_increment[case_case_increment_special]",
                    "test_inject_case_parametrizes_test_functions.py::test_case_increment[case_number]",
                    "test_inject_case_parametrizes_test_functions.py::test_case_increment[case_one]",
                    "test_inject_case_parametrizes_test_functions.py::test_case_increment[case_two]",
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
    result = pytester.runpytest_subprocess("-vvv")

    assert parse_report(result.outlines) == report
