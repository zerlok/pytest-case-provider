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


class CaseCollector[T](metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def collect_cases(self) -> t.Iterable[CaseInfo[T]]:
        raise NotImplementedError


class CaseParametrizer[T](CaseCollector[T], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_case_param(self) -> inspect.Parameter:
        raise NotImplementedError
