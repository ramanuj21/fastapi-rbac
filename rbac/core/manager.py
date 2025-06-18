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
    """
    Core class to manage Role-Based Access Control operations.
    Supports user, role, and permission management along with
    Static and Dynamic Separation of Duty (SSD/DSD) constraints.
    """
    def __init__(
        self,
        storage: AbstractStorage,
        ssd_constraint: AbstractSSDConstraint = None,
        dsd_constraint: DSDConstraint = None
    ):
        """
        Initialize the RBACManager with a storage backend and optional constraints.
        """
        self.storage = storage
        self.ssd = ssd_constraint or InMemorySSDConstraint()
        self.dsd = dsd_constraint or InMemoryDSDConstraint()
        logger.debug("RBACManager initialized with storage: %s", type(storage).__name__)

    def add_user(self, username: str) -> User:
        """
        Create and store a new user. Raises ValueError if the user already exists.
        """
        if self.storage.get_user(username):
            logger.warning("Attempt to add existing user: %s", username)
            raise ValueError(f"User '{username}' already exists.")
        user = User(username)
        self.storage.save_user(user)
        logger.info("User created: %s", username)
        return user

    def add_role(self, role: Role) -> Role:
        """
        Add a new role. Raises ValueError if the role already exists.
        """
        if self.storage.get_role(role.name):
            logger.warning("Attempt to add existing role: %s", role.name)
            raise ValueError(f"Role '{role.name}' already exists.")
        self.storage.save_role(role)
        logger.info("Role added: %s", role.name)
        return role

    def add_permission(self, perm_name: str) -> Permission:
        """
        Add a new permission. Raises ValueError if the permission already exists.
        """
        if self.storage.get_permission(perm_name):
            logger.warning("Attempt to add existing permission: %s", perm_name)
            raise ValueError(f"Permission '{perm_name}' already exists.")
        permission = Permission(perm_name)
        self.storage.save_permission(permission)
        logger.info("Permission added: %s", perm_name)
        return permission

    def assign_role(self, username: str, role_name: str) -> None:
        """
        Assign a role to a user, checking for SSD constraint violations.
        """
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
            logger.warning("SSD violation: cannot assign role '%s' to '%s'", role_name, username)
            raise ValueError(f"SSD violation: Cannot assign role '{role_name}' to '{username}'")

        user.add_role(role)
        self.storage.save_user(user)
        logger.info("Assigned role '%s' to user '%s'", role_name, username)

    def grant_permission(self, role_name: str, perm_name: str) -> None:
        """
        Grant a permission to a role. Raises error if role or permission is not found.
        """
        role = self.storage.get_role(role_name)
        permission = self.storage.get_permission(perm_name)
        if not role:
            logger.error("Role not found: %s", role_name)
            raise ValueError(f"Role '{role_name}' not found.")
        if not permission:
            logger.error("Permission not found: %s", perm_name)
            raise ValueError(f"Permission '{perm_name}' not found.")
        role.add_permission(permission)
        self.storage.save_role(role)
        logger.info("Granted permission '%s' to role '%s'", perm_name, role_name)

    def check_permission(self, username: str, perm_name: str) -> bool:
        """
        Directly check if a user has a permission (without inheritance).
        """
        user = self.storage.get_user(username)
        permission = self.storage.get_permission(perm_name)
        if not user:
            logger.error("User not found during permission check: %s", username)
            raise ValueError(f"User {username} not found.")
        if not permission:
            logger.error("Permission not found during check: %s", perm_name)
            raise ValueError(f"Permission '{perm_name}' not found.")
        result = user.has_permission(permission)
        logger.debug("Permission check for user '%s' on '%s': %s", username, perm_name, result)
        return result

    def user_has_permission(self, username: str, permission_name: str) -> bool:
        """
        Recursively checks whether a user has a permission through role inheritance.
        Cycles in role hierarchy are detected and avoided.
        """
        logger.info("Checking permission for user '%s' on '%s'", username, permission_name)
        user = self.storage.get_user(username)
        if not user:
            logger.error("User not found during permission check: %s", username)
            return False

        def has_permission(role: Role, path_stack: set[Role]) -> bool:
            if role in path_stack:
                logger.debug("Detected cycle in role inheritance for role '%s'", role.name)
                return False

            path_stack.add(role)

            if any(p.name == permission_name for p in role.permissions):
                logger.debug("Permission found in role '%s'", role.name)
                return True

            return any(has_permission(parent, path_stack.copy()) for parent in role.parents)

        return any(has_permission(role, set()) for role in user.roles)

    def get_user_permissions(self, username: str) -> set[str]:
        """
        Returns a set of permission names assigned to a user (including inherited).
        """
        user = self.storage.get_user(username)
        if not user:
            logger.error("User '%s' not found during permission enumeration", username)
            return set()

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

        logger.debug("Permissions for user '%s': %s", username, permissions)
        return permissions

    def create_session(self, username: str, active_role_names: set[str]) -> Session:
        """
        Creates a new session with a subset of the user's roles (active set).
        Validates against DSD constraints.
        """
        user = self.storage.get_user(username)
        if not user:
            logger.error("User '%s' not found during session creation", username)
            raise ValueError(f"User '{username}' not found.")

        assigned_roles = user.get_role_names()
        if not active_role_names <= assigned_roles:
            logger.warning("Attempt to activate unassigned roles for user '%s'", username)
            raise ValueError("Trying to activate roles not assigned to the user.")

        if self.dsd and not self.dsd.is_valid_activation(active_role_names):
            logger.warning("DSD violation for user '%s': roles=%s", username, active_role_names)
            raise ValueError(f"DSD violation: Conflicting roles activated together.")

        logger.info("Session created for user '%s' with roles %s", username, active_role_names)
        return Session(user=user, active_roles=set(active_role_names))
