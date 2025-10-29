import inspect
import typing as t
from functools import WRAPPER_ASSIGNMENTS, partial, update_wrapper, wraps

from typing_extensions import Concatenate, ParamSpec, Self, override

from pytest_case_provider.abc import CaseCollector, CaseParametrizer
from pytest_case_provider.case.storage import CompositeCaseStorage

U = ParamSpec("U")
V_co = t.TypeVar("V_co", covariant=True)
T_co = t.TypeVar("T_co", covariant=True)
S_contra = t.TypeVar("S_contra", contravariant=True)


# NOTE: `__globals__` is used by pytest marks such as `pytest.mark.skipif` to evaluate string condition.
_TEST_FUNC_WRAPPER_ASSIGNMENT: t.Final[t.Sequence[str]] = [*WRAPPER_ASSIGNMENTS, "__globals__"]


class FuncCaseDecorator(CompositeCaseStorage[T_co], CaseParametrizer[T_co], t.Generic[U, V_co, T_co]):
    def __init__(self, testfunc: t.Callable[Concatenate[T_co, U], V_co]) -> None:
        super().__init__()
        self.__testfunc = testfunc
        update_wrapper(self, self.__testfunc, assigned=_TEST_FUNC_WRAPPER_ASSIGNMENT)

    @override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testfunc}>"

    def __call__(self, *args: U.args, **kwargs: U.kwargs) -> V_co:
        # NOTE: `T` should be provided in `kwargs` by pytest fixture injection
        return self.__testfunc(*args, **kwargs)  # type: ignore[arg-type]

    @override
    def get_case_param(self) -> inspect.Parameter:
        return next(iter(inspect.signature(self.__testfunc).parameters.values()))


class MethodCaseDecorator(CompositeCaseStorage[T_co], CaseParametrizer[T_co], t.Generic[U, V_co, T_co, S_contra]):
    def __init__(self, testmethod: t.Callable[Concatenate[S_contra, T_co, U], V_co]) -> None:
        super().__init__()
        self.__testmethod = testmethod
        update_wrapper(self, self.__testmethod)

    @override
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} of {self.__testmethod}>"

    @t.overload
    def __get__(self, instance: None, owner: type[S_contra]) -> Self: ...

    @t.overload
    def __get__(self, instance: S_contra, owner: type[S_contra]) -> t.Callable[Concatenate[T_co, U], V_co]: ...

    def __get__(
        self,
        instance: t.Optional[S_contra],
        owner: type[S_contra],
    ) -> t.Union[Self, t.Callable[Concatenate[T_co, U], V_co]]:
        return (
            wraps(self.__testmethod, assigned=_TEST_FUNC_WRAPPER_ASSIGNMENT)(partial(self, instance))
            if instance is not None
            else self
        )

    def __call__(self, instance: S_contra, *args: U.args, **kwargs: U.kwargs) -> V_co:
        # NOTE: `T` should be provided in `kwargs` by pytest fixture injection
        return self.__testmethod(instance, *args, **kwargs)  # type: ignore[arg-type]

    @override
    def get_case_param(self) -> inspect.Parameter:
        params = iter(inspect.signature(self.__testmethod).parameters.values())
        _ = next(params)  # skip `self`
        return next(params)


class TestFuncCaseInjector(t.Generic[T_co]):
    def __init__(self, includes: t.Sequence[CaseCollector[T_co]]) -> None:
        self.__includes = includes

    def __call__(self, testfunc: t.Callable[Concatenate[T_co, U], V_co]) -> FuncCaseDecorator[U, V_co, T_co]:
        collector = FuncCaseDecorator[U, V_co, T_co](testfunc)
        collector.include(*self.__includes)
        return collector


class TestMethodCaseInjector(t.Generic[T_co]):
    def __init__(self, includes: t.Sequence[CaseCollector[T_co]]) -> None:
        self.__includes = includes

    def __call__(
        self,
        testmethod: t.Callable[Concatenate[S_contra, T_co, U], V_co],
    ) -> MethodCaseDecorator[U, V_co, T_co, S_contra]:
        collector = MethodCaseDecorator[U, V_co, T_co, S_contra](testmethod)
        collector.include(*self.__includes)
        return collector


@t.overload
def inject_cases(testfunc: t.Callable[Concatenate[T_co, U], V_co]) -> FuncCaseDecorator[U, V_co, T_co]: ...


@t.overload
def inject_cases(*includes: CaseCollector[T_co]) -> TestFuncCaseInjector[T_co]: ...


def inject_cases(
    testfunc: t.Union[t.Callable[Concatenate[T_co, U], V_co], CaseCollector[T_co], None] = None,
    *includes: CaseCollector[T_co],
) -> t.Union[FuncCaseDecorator[U, V_co, T_co], TestFuncCaseInjector[T_co]]:
    if isinstance(testfunc, CaseCollector):
        return TestFuncCaseInjector((testfunc, *includes))

    else:
        injector = TestFuncCaseInjector(includes)
        return injector(testfunc) if testfunc is not None else injector


@t.overload
def inject_cases_method(
    testmethod: t.Callable[Concatenate[S_contra, T_co, U], V_co],
) -> MethodCaseDecorator[U, V_co, T_co, S_contra]: ...


@t.overload
def inject_cases_method(*includes: CaseCollector[T_co]) -> TestMethodCaseInjector[T_co]: ...


def inject_cases_method(
    testmethod: t.Union[t.Callable[Concatenate[S_contra, T_co, U], V_co], CaseCollector[T_co], None] = None,
    *includes: CaseCollector[T_co],
) -> t.Union[MethodCaseDecorator[U, V_co, T_co, S_contra], TestMethodCaseInjector[T_co]]:
    if isinstance(testmethod, CaseCollector):
        return TestMethodCaseInjector((testmethod, *includes))

    else:
        injector = TestMethodCaseInjector(includes)
        return injector(testmethod) if testmethod is not None else injector
