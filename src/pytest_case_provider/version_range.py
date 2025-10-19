import typing as t

from pytest_case_provider.abc import ConditionalMark


class PythonVersionRange(ConditionalMark):
    def __init__(
        self,
        since: t.Sequence[int],
        until: t.Optional[t.Sequence[int]] = None,
    ) -> None:
        self.__since = tuple(since)
        self.__until = tuple(until or ())

    def __version_to_str(self, value: t.Sequence[int]) -> str:
        return ".".join(str(val) for val in value)

    @t.override
    def build_condition(self) -> str:
        expr = f"{self.__since!r} <= sys.version_info"

        if self.__until:
            expr = f"{expr} < {self.__until!r}"

        return expr

    @t.override
    def to_reason_str(self) -> str:
        text = f"Python >= {self.__version_to_str(self.__since)}"

        if self.__until:
            text += f" and < {self.__version_to_str(self.__until)}"

        return text
