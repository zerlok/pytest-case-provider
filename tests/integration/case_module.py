import asyncio
import typing as t


def case_int_42() -> int:
    return 42


async def case_async_int_43() -> int:
    await asyncio.sleep(0)
    return 43


def case_seq_int_42() -> list[int]:
    return [42]


async def case_async_seq_int_42_times_1() -> t.AsyncIterator[list[int]]:
    await asyncio.sleep(0)
    yield [1] * 42
