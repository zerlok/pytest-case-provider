import inspect
import typing as t
from functools import wraps

from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.model import CaseInfo, CaseProviderFunc
from pytest_case_provider.storage import CaseStorage


class ParametrizedTestFunction[**U, V, T](CaseCollector):
    def __init__(
        self,
        case_param_name: str,
        testfunc: t.Callable[U, V],
        cases: CaseStorage[T],
        case_param_type: t.Optional[type[T]] = None,
    ) -> None:
        self.__case_param_name = case_param_name
        self.__testfunc = testfunc
        self.__cases = cases
        self.__case_param_type = case_param_type

    def __call__(self, provide_case: T, *args: U.args, **kwargs: U.kwargs) -> V:
        if self.__case_param_type is not None and not isinstance(provide_case, self.__case_param_type):
            msg = "provided case is not of valid type"
            raise TypeError(msg, provide_case)

        kwargs[self.__case_param_name] = provide_case

        return self.__testfunc(*args, **kwargs)

    @t.override
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        return self.__cases

    def case[**S](
        self,
        name: t.Optional[str] = None,
    ) -> t.Callable[[CaseProviderFunc[S, T]], CaseProviderFunc[S, T]]:
        return self.__cases.case(name=name)

    def include(self, *others: CaseStorage[T]) -> t.Self:
        self.__cases.extend(*others)
        return self


def parametrize_cases[**U, V, T](
    testfunc: t.Callable[t.Concatenate[T, U], V],
) -> ParametrizedTestFunction[U, V, T]:
    sig = inspect.signature(testfunc)

    wrapped_params = list(sig.parameters.values())
    case_param, wrapped_params[0] = wrapped_params[0], wrapped_params[0].replace(name="provide_case")

    parametrized = ParametrizedTestFunction(case_param.name, testfunc, CaseStorage[T](), case_param.annotation)

    wrapped = wraps(testfunc)(parametrized)
    wrapped.__signature__ = sig.replace(parameters=wrapped_params)

    return wrapped
