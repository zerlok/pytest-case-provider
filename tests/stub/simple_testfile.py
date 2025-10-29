# NOTE: this file should not run by original pytest.


from pytest_case_provider import inject_cases


@inject_cases()
def test_ok_42_injected(number: int) -> None:
    assert number == 42  # noqa: PLR2004


@test_ok_42_injected.case()
def case_42() -> int:
    return 42


@inject_cases()
def test_error_injected(number: int) -> None:
    assert True


@test_error_injected.case()
def case_raises_error() -> int:
    msg = "case failed"
    raise RuntimeError(msg)
