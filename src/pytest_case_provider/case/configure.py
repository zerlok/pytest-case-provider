import inspect
import typing as t

from typing_extensions import Concatenate, ParamSpec

from pytest_case_provider.case.abc import CaseCollector, CaseStorage, FuncCaseRegistry, MethodCaseRegistry

U = ParamSpec("U")
T = t.TypeVar("T")
V = t.TypeVar("V")
S = t.TypeVar("S")


def configure_testfunc_cases(
    testfunc: t.Callable[Concatenate[T, U], V],
    storage: CaseStorage[T],
    includes: t.Optional[t.Sequence[object]] = None,
) -> FuncCaseRegistry[T, U, V]:
    registry = t.cast("FuncCaseRegistry[T, U, V]", testfunc)
    registry.__pytest_case_storage__ = storage  # type: ignore[attr-defined]
    registry.__pytest_case_parameter__ = next(inspect_params(testfunc))  # type: ignore[attr-defined]
    registry.case = storage.case  # type: ignore[method-assign]
    registry.include = storage.include  # type: ignore[method-assign,assignment]

    include_cases(storage, includes)

    return registry


def configure_testmethod_cases(
    testmethod: t.Callable[Concatenate[S, T, U], V],
    storage: CaseStorage[T],
    includes: t.Optional[t.Sequence[object]] = None,
) -> MethodCaseRegistry[S, T, U, V]:
    params = inspect_params(testmethod)
    next(params)  # skip `self`

    registry = t.cast("MethodCaseRegistry[S, T, U, V]", testmethod)
    registry.__pytest_case_storage__ = storage  # type: ignore[attr-defined]
    registry.__pytest_case_parameter__ = next(params)  # type: ignore[attr-defined]
    registry.case = storage.case  # type: ignore[method-assign]
    registry.include = storage.include  # type: ignore[method-assign,assignment]

    include_cases(storage, includes)

    return registry


def include_cases(
    storage: CaseStorage[T],
    includes: t.Optional[t.Sequence[object]],
) -> None:
    for include in includes or ():
        sub: t.Optional[CaseCollector[T]] = (
            include
            if isinstance(include, CaseCollector)
            else extract_case_storage(include)
            if include is not None
            else None
        )
        if sub is not None:
            storage.include(sub)


def inspect_params(func: t.Callable[..., object]) -> t.Iterator[inspect.Parameter]:
    return iter(inspect.signature(func).parameters.values())


def extract_case_storage(obj: object) -> t.Optional[CaseStorage[T]]:
    storage = getattr(obj, "__pytest_case_storage__", None)
    return storage if isinstance(storage, CaseStorage) else None


def extract_case_parameter(obj: object) -> t.Optional[inspect.Parameter]:
    param = getattr(obj, "__pytest_case_parameter__", None)
    return param if isinstance(param, inspect.Parameter) else None
