import inspect
import typing as t

from _pytest.fixtures import FixtureDef, SubRequest
from _pytest.mark import ParameterSet
from _pytest.python import Metafunc
from _pytest.scope import _ScopeName
from typing_extensions import Concatenate, ParamSpec, assert_never

from pytest_case_provider.inspect import get_func_kind

U = ParamSpec("U")
V_co = t.TypeVar("V_co", covariant=True)


def parametrize_metafunc_with_fixture_params(
    metafunc: Metafunc,
    name: str,
    fixture_func: t.Callable[Concatenate[SubRequest, U], V_co],
    params: t.Sequence[ParameterSet],
    scope: t.Optional[_ScopeName] = None,
) -> None:
    metafunc.parametrize(name, params, scope=scope, indirect=True)

    # NOTE: repeat FixtureManager._register_fixture logic
    fixture_defs = metafunc._arg2fixturedefs[name] = list(metafunc._arg2fixturedefs.get(name, []))  # noqa: SLF001
    fixture_defs.append(
        FixtureDef(
            config=metafunc.config,
            baseid="",
            argname=name,
            func=fixture_func,  # use provided fixture func
            scope=scope,
            params=None,  # parameters will be injected via `metafunc.parametrize`
            _ispytest=True,  # suppress deprecation warnings
        )
    )


def invoke_with_fixture_values(request: SubRequest, func: t.Callable[U, V_co]) -> V_co:
    params = list(inspect.signature(func).parameters.values())
    kind = get_func_kind(func)

    if kind == "module-function" or kind == "static-method" or kind == "local-function":  # noqa: PLR1714
        args = []
        kwargs = {param.name: request.getfixturevalue(param.name) for param in params}

    elif kind == "class-function":
        args = [request.instance]
        kwargs = {param.name: request.getfixturevalue(param.name) for param in params[1:]}

    elif kind == "class-method":
        args = [type(request.instance)]
        kwargs = {param.name: request.getfixturevalue(param.name) for param in params[1:]}

    else:
        assert_never(kind)

    return func(*args, **kwargs)
