import abc
import inspect
import typing as t
from functools import cache

from _pytest.mark.structures import get_unpacked_marks
from typing_extensions import TypeGuard, override

from pytest_case_provider.case.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc

T = t.TypeVar("T")


class InspectingCaseCollector(CaseCollector[T]):
    def __init__(self, obj: object, of_type: type[T]) -> None:
        self.__obj = obj
        self.__of_type = _normalize_type(of_type)

    @override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        for name, member in inspect.getmembers(self.__obj):
            if self.__check_returns(member):
                yield CaseInfo(
                    name=name,
                    provider=CaseProvider(member),
                    marks=get_unpacked_marks(member),
                )

    def __check_returns(self, obj: object) -> TypeGuard[CaseProviderFunc[t.Any, T]]:
        if not callable(obj):
            return False

        ret = inspect.signature(obj).return_annotation
        if ret is None:
            return False

        if inspect.isasyncgenfunction(obj) or inspect.isgeneratorfunction(obj):
            gen_origin = t.get_origin(ret)
            unwrapped = (
                t.get_args(ret)[0]
                if isinstance(gen_origin, type) and issubclass(gen_origin, (t.Iterator, t.AsyncIterator))
                else None
            )

        else:
            unwrapped = ret

        origin = t.get_origin(unwrapped)
        return (isinstance(unwrapped, type) and issubclass(unwrapped, self.__of_type)) or (
            isinstance(origin, type) and issubclass(origin, self.__of_type)
        )


class SupportsDefaultInit(t.Protocol):
    @abc.abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError


def collect_cases_class(class_: type[SupportsDefaultInit], of_type: type[T]) -> CaseCollector[T]:
    return InspectingCaseCollector(_get_instance(class_), of_type)


@cache
def _get_instance(class_: type[SupportsDefaultInit]) -> object:
    return class_()


def _normalize_type(of_type: type[T]) -> type[T]:
    try:
        _ = issubclass(object, of_type)

    except TypeError:
        origin = t.get_origin(of_type)
        try:
            _ = issubclass(
                object,
                origin,  # type: ignore[arg-type]
            )

        except (TypeError, ValueError) as err:
            msg = "can't use provided type for case inspection"
            raise TypeError(msg, of_type) from err

        else:
            return t.cast("type[T]", origin)

    else:
        return of_type
