import typing as t
from dataclasses import dataclass, field

from _pytest.mark import Mark, MarkDecorator

from pytest_case_provider.case.provider import CaseProvider

T = t.TypeVar("T")


@dataclass(frozen=True)
class CaseInfo(t.Generic[T]):
    name: str
    provider: CaseProvider[T]
    marks: t.Sequence[t.Union[Mark, MarkDecorator]] = field(default_factory=tuple)
