from abc import ABC, abstractmethod
from typing import Set, Dict

class DSDConstraint(ABC):
    """
    Abstract base class for defining Dynamic Separation of Duty (DSD) constraints.
    These constraints prevent activating conflicting roles together in a single session.
    """

    @abstractmethod
    def is_valid_assignment(self, username: str, role: str, current_roles: Set[str]) -> bool:
        """
        Optional: Validate if assigning `role` to `username` (with existing roles) violates DSD.
        Typically used during role assignment.
        """
        raise NotImplementedError("is_valid_assignment() must be implemented")

    @abstractmethod
    def is_valid_activation(self, active_roles: Set[str]) -> bool:
        """
        Validate if the given set of active roles can be used together in a session.
        """
        raise NotImplementedError("is_valid_activation() must be implemented")

    @abstractmethod
    def add_set(self, name: str, roles: Set[str]) -> None:
        """
        Add a named DSD constraint set. Roles in this set should not be active together in a session.
        """
        raise NotImplementedError("add_set() must be implemented")

    @abstractmethod
    def remove_set(self, name: str) -> None:
        """
        Remove a DSD set by its name.
        """
        raise NotImplementedError("remove_set() must be implemented")

    @abstractmethod
    def get_conflict_sets(self) -> Dict[str, Set[str]]:
        """
        Retrieve all defined DSD sets and their roles.
        """
        raise NotImplementedError("get_conflict_sets() must be implemented")
