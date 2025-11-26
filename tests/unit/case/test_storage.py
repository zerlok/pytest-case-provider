import typing as t

import pytest

from pytest_case_provider.case.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc
from pytest_case_provider.case.storage import CompositeCaseStorage, SimpleCaseStorage
from tests.stub.provider_func import provide_fixture_int, provide_int, provide_int_async

T = t.TypeVar("T")


def test_case_storage_collects_items(
    case_storage: SimpleCaseStorage[int], case_items: t.Sequence[CaseInfo[int]]
) -> None:
    # storage is empty
    assert_collected_items(case_storage, [])

    # new item added to storage
    case_storage.append(provide_int)
    assert_collected_items(case_storage, [provide_int])

    # old item remains in storage
    case_storage.append(provide_int_async)
    assert_collected_items(case_storage, [provide_int, provide_int_async])

    # case decorator appends to storage
    @case_storage.case()
    def custom_provider() -> int:
        return 0

    assert_collected_items(case_storage, [provide_int, provide_int_async, custom_provider])


def test_composite_case_storage_collects_items(
    case_storage: SimpleCaseStorage[int],
    case_sub_storage: SimpleCaseStorage[int],
    composite_case_storage: CompositeCaseStorage[int],
) -> None:
    # storage is empty
    assert_collected_items(composite_case_storage, [])

    # new item added to storage
    composite_case_storage.case()(provide_int)
    assert_collected_items(composite_case_storage, [provide_int])

    # composite storage includes cases from sub storage
    composite_case_storage.include(case_sub_storage)
    assert_collected_items(composite_case_storage, [provide_int])

    # new items in sub storage appears in composite storage
    case_sub_storage.append(provide_fixture_int)
    assert_collected_items(composite_case_storage, [provide_int, provide_fixture_int])


@pytest.fixture
def case_storage() -> SimpleCaseStorage[int]:
    return SimpleCaseStorage[int]()


@pytest.fixture
def case_items() -> t.Sequence[CaseInfo[int]]:
    store = SimpleCaseStorage[int]()

    @store.case()
    def custom_item() -> int:
        return 42

    return list(store.collect_cases())


@pytest.fixture
def case_sub_storage() -> SimpleCaseStorage[int]:
    return SimpleCaseStorage[int]()


@pytest.fixture
def composite_case_storage() -> CompositeCaseStorage[int]:
    return CompositeCaseStorage[int]()


def assert_collected_items(
    collector: CaseCollector[T],
    items: t.Sequence[t.Union[CaseInfo[T], CaseProviderFunc[t.Any, T]]],
) -> None:
    assert [str(case.provider) for case in collector.collect_cases()] == [
        str(item.provider) if isinstance(item, CaseInfo) else str(CaseProvider(item)) for item in items
    ]
