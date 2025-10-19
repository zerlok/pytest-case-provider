import pytest
from _pytest.mark import MarkDecorator

from pytest_case_provider.abc import ConditionalMark


class FeatureFlagMark:
    def __init__(self, feature: str, flag: ConditionalMark) -> None:
        self.__feature = feature
        self.__flag = flag

    def mark_required(self) -> MarkDecorator:
        return pytest.mark.skipif(
            condition=f"not ({self.__flag.build_condition()})",
            reason=f"{self.__feature} requires {self.__flag.to_reason_str()}",
        )

    def mark_obsolete(self) -> MarkDecorator:
        return pytest.mark.skipif(
            condition=self.__flag.build_condition(),
            reason=f"Obsolete since {self.__feature} is available in {self.__flag.to_reason_str()}",
        )
