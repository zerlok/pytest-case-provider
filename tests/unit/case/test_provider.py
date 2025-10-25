import inspect

import pytest
from _pytest.fixtures import SubRequest

from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc
from tests.stub.provider_func import (
    provide_fixture_int,
    provide_fixture_int_async,
    provide_fixture_int_async_iter,
    provide_fixture_int_iter,
    provide_int,
    provide_int_async,
    provide_int_async_iter,
    provide_int_iter,
)

_SIMPLE_INT_VALUE = 42
_SPECIAL_INT_VALUE = _SIMPLE_INT_VALUE**2


@pytest.mark.parametrize(
    "func",
    [
        provide_int,
        provide_int_iter,
        provide_int_async,
        provide_int_async_iter,
        provide_fixture_int,
        provide_fixture_int_iter,
        provide_fixture_int_async,
        provide_fixture_int_async_iter,
    ],
)
def test_case_provider_signature(
    provider: CaseProvider[int],
    func: CaseProviderFunc[int],
) -> None:
    assert provider.signature == inspect.signature(func)


@pytest.mark.parametrize(
    ("func", "expected_is_async"),
    [
        pytest.param(provide_int, False),
        pytest.param(provide_int_iter, False),
        pytest.param(provide_int_async, True),
        pytest.param(provide_int_async_iter, True),
        pytest.param(provide_fixture_int, False),
        pytest.param(provide_fixture_int_iter, False),
        pytest.param(provide_fixture_int_async, True),
        pytest.param(provide_fixture_int_async_iter, True),
    ],
)
def test_case_provider_is_async(
    provider: CaseProvider[int],
    expected_is_async: bool,
) -> None:
    assert provider.is_async == expected_is_async


@pytest.mark.parametrize(
    ("func", "expected_value"),
    [
        pytest.param(provide_int, _SIMPLE_INT_VALUE),
        pytest.param(provide_int_iter, _SIMPLE_INT_VALUE),
        pytest.param(provide_fixture_int, _SPECIAL_INT_VALUE),
        pytest.param(provide_fixture_int_iter, _SPECIAL_INT_VALUE),
    ],
)
def test_case_provider_provide_sync(
    request: SubRequest,
    provider: CaseProvider[int],
    expected_value: int,
) -> None:
    with provider.provide_sync(request) as value:
        assert value == expected_value


@pytest.mark.parametrize(
    ("func", "expected_value"),
    [
        pytest.param(provide_int, _SIMPLE_INT_VALUE),
        pytest.param(provide_int_iter, _SIMPLE_INT_VALUE),
        pytest.param(provide_int_async, _SIMPLE_INT_VALUE),
        pytest.param(provide_int_async_iter, _SIMPLE_INT_VALUE),
        pytest.param(provide_fixture_int, _SPECIAL_INT_VALUE),
        pytest.param(provide_fixture_int_iter, _SPECIAL_INT_VALUE),
        pytest.param(provide_fixture_int_async, _SPECIAL_INT_VALUE),
        pytest.param(provide_fixture_int_async_iter, _SPECIAL_INT_VALUE),
    ],
)
async def test_case_provider_provide_async(
    request: SubRequest,
    provider: CaseProvider[int],
    expected_value: int,
) -> None:
    async with provider.provide_async(request) as value:
        assert value == expected_value


# NOTE: special fixture to test value injection into provider
@pytest.fixture
def stub_provide_fixture_int_value() -> int:
    return _SPECIAL_INT_VALUE


@pytest.fixture
def provider(func: CaseProviderFunc[int]) -> CaseProvider[int]:
    return CaseProvider(func)
