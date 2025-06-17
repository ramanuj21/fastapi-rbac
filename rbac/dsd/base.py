from abc import ABC, abstractmethod
from typing import Set, Dict

class DSDConstraint(ABC):
    @abstractmethod
    def is_valid_assignment(self, username: str, role: str, current_roles: Set[str]) -> bool:
        ...

    @abstractmethod
    def is_valid_activation(self, active_roles: Set[str]) -> bool:
        ...

    @abstractmethod
    def add_set(self, name: str, roles: Set[str]) -> None:
        ...

    @abstractmethod
    def remove_set(self, name: str) -> None:
        ...

    @abstractmethod
    def get_conflict_sets(self) -> Dict[str, Set[str]]:
        ...
