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


def parse_report(prefix: str, outlines: t.Sequence[str]) -> Report:
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
            status2collection[status].add(match.group("name").removeprefix(prefix))

    return report


@pytest.mark.parametrize(
    ("path", "report"),
    [
        pytest.param(
            Path(__file__).parent / "test_inject_cases.py",
            Report(
                passed={
                    "::TestClass::test_class_case_injected[case_class_special_number]",
                    "::TestClass::test_class_case_injected[case_seven]",
                    "::TestClass::test_class_case_injected[case_six]",
                    "::TestClass::test_class_case_injected[case_yield_eight]",
                    "::TestClass::test_class_cases_included[case_class_special_number]",
                    "::TestClass::test_class_cases_included[case_seven]",
                    "::TestClass::test_class_cases_included[case_six]",
                    "::TestClass::test_class_cases_included[case_yield_eight]",
                    "::TestClass::test_without_case_injection",
                    "::TestClassAsync::test_async_class_case_injected[case_async_nine]",
                    "::TestClassAsync::test_async_class_case_injected[case_async_yield_ten]",
                    "::test_case_injected[case_async_three_for_sync_test]",
                    "::test_case_injected[case_async_yield_five_for_sync_test]",
                    "::test_case_injected[case_one]",
                    "::test_case_injected[case_special_number]",
                    "::test_case_injected[case_two]",
                    "::test_case_injected[case_yield_four]",
                    "::test_cases_included_to_fixture[case_async_three_for_sync_test]",
                    "::test_cases_included_to_fixture[case_async_yield_five_for_sync_test]",
                    "::test_cases_included_to_fixture[case_case_minus_one]",
                    "::test_cases_included_to_fixture[case_one]",
                    "::test_cases_included_to_fixture[case_special_number]",
                    "::test_cases_included_to_fixture[case_two]",
                    "::test_cases_included_to_fixture[case_yield_four]",
                    "::test_without_case_injection",
                },
                skipped={
                    "::TestClass::test_no_case_injected[NOTSET]",
                    "::test_case_injected[case_skipped]",
                    "::test_cases_included_to_fixture[case_skipped]",
                    "::test_no_case_injected[NOTSET]",
                },
                failed=set(),
                error=set(),
                xfail=set(),
                xpass=set(),
            ),
            id="test_inject_case.py report",
        ),
        pytest.param(
            Path(__file__).parent / "test_marks.py",
            Report(
                passed={
                    "::test_obsoletes_python2",
                    "::test_requires_python3",
                    "::test_runs_only_when_bar_toggle_on",
                    "::test_runs_only_when_foo_toggle_off",
                },
                skipped={
                    "::test_obsoletes_python3",
                    "::test_requires_python2",
                    "::test_runs_only_when_bar_toggle_off",
                    "::test_runs_only_when_foo_toggle_on",
                },
                failed=set(),
                error=set(),
                xfail=set(),
                xpass=set(),
            ),
            id="test_marks.py report",
        ),
    ],
)
def test_inject_case_parametrizes_test_functions(pytester: Pytester, path: Path, report: Report) -> None:
    path = pytester.makepyfile(path.read_text())
    result = pytester.runpytest_subprocess("-vvv", "--asyncio-mode=auto")

    assert parse_report(path.name, result.outlines) == report
