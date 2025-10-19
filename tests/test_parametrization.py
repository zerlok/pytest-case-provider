from dataclasses import dataclass

from _pytest.fixtures import SubRequest

from pytest_case_provider.parametrize import parametrize_cases


@dataclass(frozen=True, kw_only=True)
class MyCase:
    foo: int


def test_x() -> None:
    assert True


@parametrize_cases
def test_simple(request: SubRequest, case: MyCase) -> None:
    assert isinstance(case, MyCase)


@test_simple.case()
def case_one() -> MyCase:
    return MyCase(foo=1)


@test_simple.case()
def case_two() -> MyCase:
    return MyCase(foo=2)
