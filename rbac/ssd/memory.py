from typing import Optional, Set, Dict
from .base import AbstractSSDConstraint

class InMemorySSDConstraint(AbstractSSDConstraint):
    def __init__(self, conflict_sets: Optional[Dict[str, Set[str]]] = None):
        self.conflict_sets = conflict_sets or {}

    def add_set(self, name: str, roles: Set[str]) -> None:
        self.conflict_sets[name] = roles

    def remove_set(self, name: str) -> None:
        if name in self.conflict_sets:
            del self.conflict_sets[name]
        else:
            raise ValueError(f"SSD set '{name}' not found")

    def get_all_sets(self) -> dict[str, list[str]]:
        return {name: list(roles) for name, roles in self.conflict_sets.items()}


    def is_valid_assignment(self, username: str, new_role: str, current_roles: set[str]) -> bool:
        proposed_roles = set(current_roles) | {new_role}
        return not self.is_conflicting(proposed_roles)

    def is_conflicting(self, roles: set[str]) -> bool:
        for role_set in self.conflict_sets.values():
            if len(role_set & roles) > 1:
                return True
        return False


