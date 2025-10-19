# pytest-case-provider

**pytest-case-provider** is a lightweight plugin that extends `pytest.mark.parametrize` with declarative *case factories* — functions that produce structured test inputs, optionally async and fixture-aware.

It allows defining test cases as standalone callables that can depend on other fixtures and produce complex test objects, while keeping tests clean and expressive.

---

## Features

- Define test cases as sync or async factory functions
- Access pytest fixtures directly inside case factories
- Works seamlessly with regular `pytest.mark.parametrize`
- Automatic case discovery and parametrization via plugin hooks
- Full type support (works with `mypy` and modern type checkers)

---

## Example

```python
import asyncio
from dataclasses import dataclass
from pytest_case_provider import with_parametrization
from pytest import SubRequest


@dataclass(frozen=True)
class MyCase:
    foo: int


@with_parametrization(MyCase)
def test_example(case: MyCase) -> None:
    assert isinstance(case, MyCase)


@test_example.case()
def case_sync() -> MyCase:
    return MyCase(foo=1)


@test_example.case()
async def case_async(request: SubRequest) -> MyCase:
    await asyncio.sleep(0.1)
    return MyCase(foo=2)
