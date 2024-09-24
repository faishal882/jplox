from abc import ABC, abstractmethod

class LoxCallable(ABC):
    @abstractmethod
    def arity(self)->int:
        pass

    @abstractmethod
    def call(self, interpreter, arguments):
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

