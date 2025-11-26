import abc


class ConditionalMark(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build_condition(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def to_reason_str(self) -> str:
        raise NotImplementedError
