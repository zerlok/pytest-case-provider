import sys

import pytest

from tests.stub.feature import (
    FEATURE_BAR_ENABLED,
    FEATURE_FOO_DISABLED,
    FEATURE_PYTHON_2,
    FEATURE_PYTHON_3,
    TOGGLE_BAR_ON,
    TOGGLE_FOO_OFF,
)


@FEATURE_PYTHON_3.mark_required()
def test_requires_python3() -> None:
    assert sys.version_info >= (3,)


@FEATURE_PYTHON_3.mark_obsolete()
def test_obsoletes_python3() -> None:
    pytest.fail("not a python3, thus should not run this test")


@FEATURE_PYTHON_2.mark_required()
def test_requires_python2() -> None:
    pytest.fail("not a python2, thus should not run this test")


@FEATURE_PYTHON_2.mark_obsolete()
def test_obsoletes_python2() -> None:
    assert sys.version_info >= (2,)


@FEATURE_FOO_DISABLED.mark_required()
def test_runs_only_when_foo_toggle_on() -> None:
    assert TOGGLE_FOO_OFF.value is True


@FEATURE_FOO_DISABLED.mark_obsolete()
def test_runs_only_when_foo_toggle_off() -> None:
    assert TOGGLE_FOO_OFF.value is False


@FEATURE_BAR_ENABLED.mark_required()
def test_runs_only_when_bar_toggle_on() -> None:
    assert TOGGLE_BAR_ON.value is True


@FEATURE_BAR_ENABLED.mark_obsolete()
def test_runs_only_when_bar_toggle_off() -> None:
    assert TOGGLE_BAR_ON.value is False
