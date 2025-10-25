import asyncio
import typing as t


def provide_int() -> int:
    return 42


def provide_int_iter() -> t.Iterator[int]:
    yield 42


async def provide_int_async() -> int:
    await asyncio.sleep(0)
    return 42


async def provide_int_async_iter() -> t.AsyncIterator[int]:
    await asyncio.sleep(0)
    yield 42


def provide_fixture_int(stub_provide_fixture_int_value: int) -> int:
    return stub_provide_fixture_int_value


def provide_fixture_int_iter(stub_provide_fixture_int_value: int) -> t.Iterator[int]:
    yield stub_provide_fixture_int_value


async def provide_fixture_int_async(stub_provide_fixture_int_value: int) -> int:
    await asyncio.sleep(0)
    return stub_provide_fixture_int_value


async def provide_fixture_int_async_iter(stub_provide_fixture_int_value: int) -> t.AsyncIterator[int]:
    await asyncio.sleep(0)
    yield stub_provide_fixture_int_value
