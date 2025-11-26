from pytest_case_provider import inject_cases_func


@inject_cases_func()
def test_got_int(case: int) -> None:
    assert isinstance(case, int)


@inject_cases_func()
def test_got_seq_int(case: list[int]) -> None:
    assert isinstance(case, list)
