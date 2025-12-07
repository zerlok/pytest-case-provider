import sys
import types
import typing as t

FuncKind = t.Literal[
    "module-function",
    "class-function",
    "class-method",
    "static-method",
    "local-function",
]


def get_func_kind(
    obj: t.Union["classmethod[object, ..., object]", "staticmethod[..., object]", t.Callable[..., t.Any]],
) -> FuncKind:
    if isinstance(obj, classmethod):
        return "class-method"
    if isinstance(obj, staticmethod):
        return "static-method"
    if isinstance(obj, types.MethodType):
        return "class-method" if isinstance(obj.__self__, type) else "class-function"
    if isinstance(obj, types.FunctionType):
        return _reveal_func_kind(obj)

    raise TypeError(type(obj))


def _reveal_func_kind(obj: types.FunctionType) -> FuncKind:
    local_scope, _, local_name = obj.__qualname__.rpartition(".<locals>.")
    if local_scope and local_name == obj.__name__:
        return "local-function"

    cls_name, _, func_name = local_name.rpartition(".")
    if cls_name and func_name == obj.__name__:
        cls = getattr(sys.modules.get(obj.__module__), cls_name, None)
        if isinstance(cls, type):
            raw = cls.__dict__.get(func_name)
            if isinstance(raw, staticmethod):
                return "static-method"
            if isinstance(raw, classmethod):
                return "class-method"
            if raw is not None:
                return "class-function"

        # fallback to class function (the only possible case here)
        return "class-function"

    return "module-function"
