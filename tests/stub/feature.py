from typing_extensions import override

from pytest_case_provider.abc import ConditionalMark
from pytest_case_provider.mark import FeatureFlagMark, VersionRange

FEATURE_PYTHON_3 = FeatureFlagMark("python3", VersionRange.python(since=(3,)))
FEATURE_PYTHON_2 = FeatureFlagMark("python2", VersionRange.python(since=(2,), until=(3,)))


class ToggleMark(ConditionalMark):
    def __init__(self, *, value: bool, reason: str) -> None:
        self.__value = value
        self.__reason = reason

    @property
    def value(self) -> bool:
        return self.__value

    @override
    def build_condition(self) -> str:
        return f"{self.__value!r}"

    @override
    def to_reason_str(self) -> str:
        return self.__reason


TOGGLE_FOO_OFF = ToggleMark(value=False, reason="custom reason")
TOGGLE_BAR_ON = ToggleMark(value=True, reason="custom reason")
FEATURE_FOO_DISABLED = FeatureFlagMark("foo disabled", TOGGLE_FOO_OFF)
FEATURE_BAR_ENABLED = FeatureFlagMark("bar enabled", TOGGLE_BAR_ON)
