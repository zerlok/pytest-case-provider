import abc
import inspect
import typing as t

from pytest_case_provider.case.info import CaseInfo


class ConditionalMark(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_condition(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def to_reason_str(self) -> str:
        raise NotImplementedError


class CaseCollector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_signature(self) -> inspect.Signature:
        raise NotImplementedError

    @abc.abstractmethod
    def collect_cases(self) -> t.Iterable[CaseInfo[object]]:
        raise NotImplementedError
