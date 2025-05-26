from abc import ABC, abstractmethod
from typing import Protocol

class ComparableData(ABC):
    @abstractmethod
    def compare(self, other: "ComparableData | None") -> bool:
        ...

class Fetchable(Protocol):
    def fetch(self) -> ComparableData:
        ...