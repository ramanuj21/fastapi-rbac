from typing import Dict, Set
from .base import DSDConstraint
import logging

logger = logging.getLogger(__name__)

class InMemoryDSDConstraint(DSDConstraint):
    """
    In-memory implementation of Dynamic Separation of Duty (DSD) constraints.
    Prevents simultaneous activation of conflicting roles in a session.
    """

    def __init__(self, conflict_sets: Dict[str, Set[str]] = None):
        """
        Initialize the constraint manager with optional predefined conflict sets.
        """
        self.conflict_sets: Dict[str, Set[str]] = conflict_sets.copy() if conflict_sets else {}

    def is_valid_assignment(self, username: str, role: str, current_roles: Set[str]) -> bool:
        """
        Optional: Prevent assignment of roles that could cause DSD violations in sessions.
        """
        for rule_name, conflicting_roles in self.conflict_sets.items():
            if role in conflicting_roles:
                overlap = conflicting_roles.intersection(current_roles | {role})
                if len(overlap) > 1:
                    logger.warning(
                        f"DSD violation during assignment: rule '{rule_name}' with roles {conflicting_roles} — attempted: {role} to {username}"
                    )
                    return False
        return True

    def is_valid_activation(self, active_roles: Set[str]) -> bool:
        """
        Check if active roles in a session violate any DSD constraints.
        """
        for rule_name, conflicting_roles in self.conflict_sets.items():
            if len(conflicting_roles.intersection(active_roles)) > 1:
                logger.warning(
                    f"DSD violation during activation: rule '{rule_name}' with roles {conflicting_roles} — attempted active roles: {active_roles}"
                )
                return False
        return True

    def add_set(self, name: str, roles: Set[str]) -> None:
        """
        Add a new DSD constraint set with a name.
        """
        self.conflict_sets[name] = roles.copy()
        logger.info(f"DSD set '{name}' added with roles: {roles}")

    def remove_set(self, name: str) -> None:
        """
        Remove a DSD constraint set by name.
        """
        if self.conflict_sets.pop(name, None) is not None:
            logger.info(f"DSD set '{name}' removed.")
        else:
            logger.debug(f"DSD set '{name}' not found. No action taken.")

    def get_conflict_sets(self) -> Dict[str, Set[str]]:
        """
        Return all defined DSD sets.
        """
        return self.conflict_sets.copy()
