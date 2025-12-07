from __future__ import annotations

import typing as t

import pytest

from pytest_case_provider.inspect import get_func_kind


class TestRevealFuncType:
    def test_module_function_is_correct(self, revealer: Revealer) -> None:
        revealer(to_string)

        assert revealer.results == ["module-function"]

    def test_local_function_is_correct(self, revealer: Revealer) -> None:
        def outer_func() -> None:
            @revealer
            def local_func() -> None:
                pass

        outer_func()  # invoke outer to invoke revealer

        assert revealer.results == ["local-function"]

    def test_instance_class_function_is_correct(self, revealer: Revealer) -> None:
        revealer(Some().do_class_func_stuff)

        assert revealer.results == ["class-function"]

    def test_instance_class_method_is_correct(self, revealer: Revealer) -> None:
        revealer(Some().do_class_method_stuff)

        assert revealer.results == ["class-method"]

    def test_instance_static_method_is_correct(self, revealer: Revealer) -> None:
        revealer(Some().do_static_method_stuff)

        assert revealer.results == ["static-method"]

    def test_class_function_is_correct(self, revealer: Revealer) -> None:
        revealer(Some.do_class_func_stuff)

        assert revealer.results == ["class-function"]

    def test_class_method_is_correct(self, revealer: Revealer) -> None:
        revealer(Some.do_class_method_stuff)

        assert revealer.results == ["class-method"]

    def test_static_method_is_correct(self, revealer: Revealer) -> None:
        revealer(Some.do_static_method_stuff)

        assert revealer.results == ["static-method"]

    def test_future_class_function_is_correct(self, revealer: Revealer) -> None:
        class Foo:
            @revealer
            def do_class_func_stuff(self) -> None:
                pass

        assert revealer.results == ["class-function"]

    def test_future_class_method_is_correct(self, revealer: Revealer) -> None:
        class Foo:
            @revealer
            @classmethod
            def do_class_method_stuff(cls) -> None:
                pass

        assert revealer.results == ["class-method"]

    def test_future_static_method_is_correct(self, revealer: Revealer) -> None:
        class Foo:
            @revealer
            @staticmethod
            def do_static_method_stuff() -> None:
                pass

        assert revealer.results == ["static-method"]


class Revealer:
    def __init__(self) -> None:
        self.__results = list[str]()

    def __call__(self, func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        self.__results.append(get_func_kind(func))
        return func

    @property
    def results(self) -> t.Sequence[str]:
        return self.__results


@pytest.fixture
def revealer() -> Revealer:
    return Revealer()


def to_string(foo: int) -> str:
    return str(foo)


class Some:
    def do_class_func_stuff(self) -> None:
        pass

    @classmethod
    def do_class_method_stuff(cls) -> None:
        pass

    @staticmethod
    def do_static_method_stuff() -> None:
        pass
