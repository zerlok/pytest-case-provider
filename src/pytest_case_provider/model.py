import typing as t
from dataclasses import dataclass, field

from _pytest.mark import MarkDecorator

type CaseProviderFunc[**U, V] = t.Union[
    t.Callable[U, V],
    t.Callable[U, t.Iterator[V]],
    t.Callable[U, t.ContextManager[V]],
    t.Callable[U, t.Coroutine[None, None, V]],
    t.Callable[U, t.AsyncIterator[V]],
    t.Callable[U, t.AsyncContextManager[V]],
]


@dataclass(frozen=True)
class CaseInfo[T]:
    name: str
    provider: CaseProviderFunc[..., T]
    marks: t.Sequence[MarkDecorator] = field(default_factory=tuple)
