from abc import ABC, abstractmethod

class AbstractSSDConstraint(ABC):
    @abstractmethod
    def add_set(self, name: str, roles: set[str]) -> None:
        pass

    @abstractmethod
    def remove_set(self, name: str) -> None:
        pass

    @abstractmethod
    def get_all_sets(self) -> dict[str, list[str]]:
        pass

    @abstractmethod
    def is_valid_assignment(self, username: str, new_role: str, current_roles: set[str]) -> bool:
        pass
