# import pytest
#
#
# def pytest_configure(config: pytest.Config) -> None:
#     config.addinivalue_line(
#         "markers", "case_provider: parametrization via case factories"
#     )
#
#
# def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
#     # Detect parametrized tests created with CaseParametrizer
#     if hasattr(metafunc.function, "__case_parametrizer__"):
#         parametrizer: CaseParametrizer = metafunc.function.__case_parametrizer__
#         params = parametrizer.collect_cases()
#         metafunc.parametrize(parametrizer.name, params)
