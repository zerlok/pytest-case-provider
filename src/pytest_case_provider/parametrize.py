import inspect
import typing as t
from contextlib import contextmanager
from functools import wraps

import pytest
from _pytest.fixtures import SubRequest

from pytest_case_provider.case import CaseStorage


class TestFunctionParametrizer[**U, V, T]:
    def __init__(
        self,
        testfunc: t.Callable[t.Concatenate[SubRequest, T, U], V],
        cases: CaseStorage[T],
    ) -> None:
        self.__testfunc = testfunc
        self.__cases = cases
        self.__case_param = list(inspect.signature(testfunc).parameters.values())[1]

    def __call__(self, request: SubRequest, *args: U.args, **kwargs: U.kwargs) -> V:
        with self.__provide_case(request) as case:
            kwargs[self._case_param_name] = case
            return self.__testfunc(request, *args, **kwargs)

    def case[**S](
        self,
        name: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable[S, T]], t.Callable[S, T]]:
        return self.__cases.case(name=name)

    @property
    def _case_param_name(self) -> str:
        return self.__case_param.name

    @contextmanager
    def __provide_case(self, request: SubRequest) -> t.Iterator[T]:
        case_provider: object = request.getfixturevalue(self._case_param_name)
        assert callable(case_provider)

        case_provider_kwargs = {
            param.name: t.cast("object", request.getfixturevalue(param.name))
            for param in inspect.signature(case_provider).parameters.values()
        }

        case: object = case_provider(**case_provider_kwargs)
        assert isinstance(case, self.__case_param.annotation)  # type: ignore[misc]

        yield t.cast("T", case)


def parametrize_cases[**U, V, T](
    testfunc: t.Callable[t.Concatenate[SubRequest, T, U], V],
) -> TestFunctionParametrizer[U, V, T]:
    cases = CaseStorage[T]()
    parametrizer = TestFunctionParametrizer(testfunc, cases)
    return pytest.mark.parametrize(parametrizer._case_param_name, cases)(wraps(testfunc)(parametrizer))
