from typing import Dict, Set
from .base import DSDConstraint
import logging

logger = logging.getLogger(__name__)

class InMemoryDSDConstraint(DSDConstraint):
    def __init__(self, conflict_sets: Dict[str, Set[str]] = None):
        self.conflict_sets: Dict[str, Set[str]] = conflict_sets or {}

    def is_valid_assignment(self, username: str, role: str, current_roles: Set[str]) -> bool:
        for rule_name, conflicting_roles in self.conflict_sets.items():
            if role in conflicting_roles:
                count = len(conflicting_roles.intersection(current_roles | {role}))
                if count > 1:
                    logger.warning(f"DSD violation during assignment: rule '{rule_name}' with roles {conflicting_roles} — attempted: {role} to {username}")
                    return False
        return True

    def is_valid_activation(self, active_roles: Set[str]) -> bool:
        for rule_name, conflicting_roles in self.conflict_sets.items():
            if len(conflicting_roles.intersection(active_roles)) > 1:
                logger.warning(f"DSD violation during activation: rule '{rule_name}' with roles {conflicting_roles} — attempted active roles: {active_roles}")
                return False
        return True

    def add_set(self, name: str, roles: Set[str]) -> None:
        self.conflict_sets[name] = roles

    def remove_set(self, name: str) -> None:
        self.conflict_sets.pop(name, None)

    def get_conflict_sets(self) -> Dict[str, Set[str]]:
        return self.conflict_sets
