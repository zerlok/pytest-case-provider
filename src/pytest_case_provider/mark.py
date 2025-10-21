import typing as t

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


class VersionRange(ConditionalMark):
    @classmethod
    def python(cls, since: t.Sequence[int], until: t.Sequence[int] | None = None) -> "VersionRange":
        return cls("Python", "sys.version_info", since, until)

    def __init__(
        self,
        name: str,
        version_expr: str,
        since: t.Sequence[int],
        until: t.Sequence[int] | None = None,
    ) -> None:
        self.__name = name
        self.__version_expr = version_expr
        self.__since = tuple(since)
        self.__until = tuple(until or ())

    def __version_to_str(self, value: t.Sequence[int]) -> str:
        return ".".join(str(val) for val in value)

    @t.override
    def build_condition(self) -> str:
        expr = f"{self.__since!r} <= {self.__version_expr}"

        if self.__until:
            expr = f"{expr} < {self.__until!r}"

        return expr

    @t.override
    def to_reason_str(self) -> str:
        text = f"{self.__name} >= {self.__version_to_str(self.__since)}"

        if self.__until:
            text += f" and < {self.__version_to_str(self.__until)}"

        return text
