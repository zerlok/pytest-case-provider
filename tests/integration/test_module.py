from pytest_case_provider import inject_func, inject_method


@inject_func()
def test_got_int(case: int) -> None:
    assert isinstance(case, int)


@inject_func()
def test_got_seq_int(case: list[int]) -> None:
    assert isinstance(case, list)


class TestGroup:
    @inject_method()
    def test_got_int(self, case: int) -> None:
        assert isinstance(case, int)
