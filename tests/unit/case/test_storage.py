import typing as t

import pytest

from pytest_case_provider import CaseStorage, CompositeCaseStorage
from pytest_case_provider.abc import CaseCollector
from pytest_case_provider.case.info import CaseInfo
from pytest_case_provider.case.provider import CaseProvider, CaseProviderFunc
from tests.stub.provider_func import (
    provide_fixture_int,
    provide_int,
    provide_int_async,
    provide_int_async_iter,
)


def test_case_storage_collects_items(case_storage: CaseStorage[int], case_items: t.Sequence[CaseInfo[int]]) -> None:
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

    # cases extended
    case_storage.extend(case_items)
    assert_collected_items(
        case_storage,
        [provide_int, provide_int_async, custom_provider, *case_items],
    )


def test_composite_case_storage_collects_items(
    case_storage: CaseStorage[int],
    case_sub_storage: CaseStorage[int],
    composite_case_storage: CompositeCaseStorage[int],
) -> None:
    # storage is empty
    assert_collected_items(composite_case_storage, [])

    # new item added to storage
    composite_case_storage.append(provide_int)
    assert_collected_items(composite_case_storage, [provide_int])

    # composite storage extended with cases
    case_storage.append(provide_int_async)
    composite_case_storage.extend(case_storage)
    assert_collected_items(composite_case_storage, [provide_int, provide_int_async])

    # extend does not include new items
    case_storage.append(provide_int_async_iter)
    assert_collected_items(composite_case_storage, [provide_int, provide_int_async])

    # composite storage includes cases from sub storage
    composite_case_storage.include(case_sub_storage)
    assert_collected_items(composite_case_storage, [provide_int, provide_int_async])

    # new items in sub storage appears in composite storage
    case_sub_storage.append(provide_fixture_int)
    assert_collected_items(composite_case_storage, [provide_int, provide_int_async, provide_fixture_int])


@pytest.fixture
def case_storage() -> CaseStorage[int]:
    return CaseStorage[int]()


@pytest.fixture
def case_items() -> t.Sequence[CaseInfo[int]]:
    store = CaseStorage[int]()

    @store.case()
    def custom_item() -> int:
        return 42

    return list(store.collect_cases())


@pytest.fixture
def case_sub_storage() -> CaseStorage[int]:
    return CaseStorage[int]()


@pytest.fixture
def composite_case_storage() -> CompositeCaseStorage[int]:
    return CompositeCaseStorage[int]()


def assert_collected_items[T](
    collector: CaseCollector[T], items: t.Sequence[t.Union[CaseInfo[T], CaseProviderFunc[..., T]]]
) -> None:
    assert [str(case.provider) for case in collector.collect_cases()] == [
        str(item.provider) if isinstance(item, CaseInfo) else str(CaseProvider(item)) for item in items
    ]
