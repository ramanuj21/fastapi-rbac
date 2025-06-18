from typing import Optional, Set, Dict
from .base import AbstractSSDConstraint

class InMemorySSDConstraint(AbstractSSDConstraint):
    """
    In-memory implementation of Static Separation of Duty (SSD) constraints.
    Stores conflict role sets and prevents assignment of conflicting roles to a user.
    """

    def __init__(self, conflict_sets: Optional[Dict[str, Set[str]]] = None):
        self.conflict_sets: Dict[str, Set[str]] = conflict_sets or {}

    def add_set(self, name: str, roles: Set[str]) -> None:
        """
        Add or update a named SSD set. Users may not be assigned more than one role from this set.
        """
        self.conflict_sets[name] = roles

    def remove_set(self, name: str) -> None:
        """
        Remove a named SSD set.
        """
        if name in self.conflict_sets:
            del self.conflict_sets[name]
        else:
            raise ValueError(f"SSD set '{name}' not found")

    def get_all_sets(self) -> dict[str, list[str]]:
        """
        Return all SSD sets in serializable format.
        """
        return {name: list(roles) for name, roles in self.conflict_sets.items()}

    def is_valid_assignment(self, username: str, new_role: str, current_roles: set[str]) -> bool:
        """
        Check if adding `new_role` to `username` with `current_roles` violates any SSD set.
        """
        proposed_roles = set(current_roles) | {new_role}
        return not self.is_conflicting(proposed_roles)

    def is_conflicting(self, roles: set[str]) -> bool:
        """
        Check if any SSD set has more than one role in `roles`.
        """
        for role_set in self.conflict_sets.values():
            if len(role_set & roles) > 1:
                return True
        return False
