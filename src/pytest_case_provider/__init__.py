__all__ = [
    "CaseStorage",
    "CompositeCaseStorage",
    "inject_cases",
    "inject_cases_method",
]

from pytest_case_provider.case.decorator import inject_cases, inject_cases_method
from pytest_case_provider.case.storage import CaseStorage, CompositeCaseStorage
