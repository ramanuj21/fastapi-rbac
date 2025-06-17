import logging
from rbac.dsd.memory import InMemoryDSDConstraint
from rbac.models import User, Role, Permission
from rbac.storage import AbstractStorage
from rbac.ssd.base import AbstractSSDConstraint
from rbac.ssd.memory import InMemorySSDConstraint
from rbac.dsd.base import DSDConstraint
from rbac.models import Session

logger = logging.getLogger(__name__)

class RBACManager:
    def __init__(self, storage: AbstractStorage, ssd_constraint: AbstractSSDConstraint = None, dsd_constraint: DSDConstraint = None):
        self.storage = storage
        self.ssd = ssd_constraint or InMemorySSDConstraint()
        self.dsd = dsd_constraint or InMemoryDSDConstraint()
        logger.debug("RBACManager initialized with storage: %s", type(storage).__name__)

    def add_user(self, username: str) -> User:
        if self.storage.get_user(username):
            logger.warning("Attempt to add existing user: %s", username)
            raise ValueError(f"User '{username}' already exists.")
        user = User(username)
        self.storage.save_user(user)
        logger.info("Added user: %s", username)
        return user

    def add_role(self, role: Role) -> Role:
        if self.storage.get_role(role.name):
            logger.warning("Attempt to add existing role: %s", role.name)
            raise ValueError(f"Role '{role.name}' already exists.")
        self.storage.save_role(role)
        logger.info("Added role: %s", role.name)
        logger.debug(self.storage)
        return role

    def add_permission(self, perm_name: str) -> Permission:
        if self.storage.get_permission(perm_name):
            logger.warning("Attempt to add existing permission: %s", perm_name)
            raise ValueError(f"Permission '{perm_name}' already exists.")
        permission = Permission(perm_name)
        self.storage.save_permission(permission)
        logger.info("Added permission: %s", perm_name)
        return permission

    def assign_role(self, username: str, role_name: str) -> None:
        user = self.storage.get_user(username)
        role = self.storage.get_role(role_name)
        if not user:
            logger.error("User not found: %s", username)
            raise ValueError(f"User '{username}' not found.")
        if not role:
            logger.error("Role not found: %s", role_name)
            raise ValueError(f"Role '{role_name}' not found.")

        current_roles = user.get_role_names()

        if self.ssd and not self.ssd.is_valid_assignment(username, role_name, current_roles):
            raise ValueError(f"SSD violation: Cannot assign role '{role_name}' to '{username}'")

        user.add_role(role)
        self.storage.save_user(user)

        logger.info("Assigned role '%s' to user '%s'", role_name, username)

    def grant_permission(self, role_name: str, perm_name: str) -> None:
        role = self.storage.get_role(role_name)
        permission = self.storage.get_permission(perm_name)
        if not role:
            logger.error("Role not found: %s", role_name)
            raise ValueError(f"Role '{role_name}' not found.")
        if not permission:
            logger.error("Permission not found: %s", perm_name)
            raise ValueError(f"Permission '{perm_name}' not found.")
        role.add_permission(permission)
        logger.info("Granted permission '%s' to role '%s'", perm_name, role_name)

    def check_permission(self, username: str, perm_name: str) -> bool:
        user = self.storage.get_user(username)
        permission = self.storage.get_permission(perm_name)
        if not user:
            logger.error("User not found during permission check: %s", username)
            raise ValueError(f"User '{username}' not found.")
        if not permission:
            logger.error("Permission not found during check: %s", perm_name)
            raise ValueError(f"Permission '{perm_name}' not found.")
        result = user.has_permission(permission)
        logger.debug("Permission check for user '%s' on '%s': %s", username, perm_name, result)
        return result

    def user_has_permission(self, username: str, permission_name: str) -> bool:
        logger.info("Checking permission for user '%s' on '%s'", username, permission_name)
        user = self.storage.get_user(username)
        if not user:
            logger.error("User not found during permission check: %s", username)
            return False

        def has_permission(role: Role, path_stack: set[Role]) -> bool:
            if role in path_stack:
                logger.debug("Detected cycle in role inheritance for role '%s'", role.name)
                return False  # Cycle detected in current path

            path_stack.add(role)

            # Check direct permissions
            if any(p.name == permission_name for p in role.permissions):
                return True

            # Recurse into parents
            for parent in role.parents:
                if has_permission(parent, path_stack.copy()):
                    return True

            return False

        for role in user.roles:
            if has_permission(role, set()):
                return True

        return False


    def get_user_permissions(self, username: str) -> set[str]:
        user = self.storage.get_user(username)
        permissions = set()

        visited_roles = set()

        def collect_permissions(role: Role):
            if role.name in visited_roles:
                return
            visited_roles.add(role.name)
            for perm in role.permissions:
                permissions.add(perm.name)
            for parent in role.parents:
                collect_permissions(parent)

        for role in user.roles:
            collect_permissions(role)

        return permissions

    def create_session(self, username: str, active_role_names: set[str]) -> Session:
        user = self.storage.get_user(username)
        if not user:
            raise ValueError(f"User '{username}' not found.")

        assigned_roles = user.get_role_names()
        if not active_role_names <= assigned_roles:
            raise ValueError("Trying to activate roles not assigned to the user.")

        if self.dsd and not self.dsd.is_valid_activation(active_role_names):
            raise ValueError(f"DSD violation: Conflicting roles activated together.")

        return Session(user=user, active_roles=set(active_role_names))
