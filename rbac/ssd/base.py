from abc import ABC, abstractmethod

class AbstractSSDConstraint(ABC):
    @abstractmethod
    def add_set(self, name: str, roles: set[str]) -> None:
        """
        Add a Static Separation of Duty (SSD) constraint set with a unique name.
        Users cannot be assigned more than one role from this set.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_set(self, name: str) -> None:
        """
        Remove an SSD constraint set by name.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_sets(self) -> dict[str, list[str]]:
        """
        Retrieve all defined SSD sets with their role members.
        """
        raise NotImplementedError

    @abstractmethod
    def is_valid_assignment(self, username: str, new_role: str, current_roles: set[str]) -> bool:
        """
        Check if assigning `new_role` to `username` (who already has `current_roles`)
        would violate any SSD constraint.
        """
        raise NotImplementedError
