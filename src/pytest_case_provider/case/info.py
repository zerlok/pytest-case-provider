import typing as t
from dataclasses import dataclass, field

from _pytest.mark import MarkDecorator

from pytest_case_provider.case.provider import CaseProvider

T = t.TypeVar("T")


@dataclass(frozen=True)
class CaseInfo(t.Generic[T]):
    name: str
    provider: CaseProvider[T]
    marks: t.Sequence[MarkDecorator] = field(default_factory=tuple)
