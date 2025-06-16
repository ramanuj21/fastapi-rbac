import logging
from rbac.models import User, Role, Permission
from rbac.storage import AbstractStorage

logger = logging.getLogger(__name__)

class RBACManager:
    def __init__(self, storage: AbstractStorage):
        self.storage = storage
        logger.debug("RBACManager initialized with storage: %s", type(storage).__name__)

    def add_user(self, username: str) -> User:
        if self.storage.get_user(username):
            logger.warning("Attempt to add existing user: %s", username)
            raise ValueError(f"User '{username}' already exists.")
        user = User(username)
        self.storage.save_user(user)
        logger.info("Added user: %s", username)
        return user

    def add_role(self, role_name: str) -> Role:
        if self.storage.get_role(role_name):
            logger.warning("Attempt to add existing role: %s", role_name)
            raise ValueError(f"Role '{role_name}' already exists.")
        role = Role(role_name)
        self.storage.save_role(role)
        logger.info("Added role: %s", role_name)
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
        user.add_role(role)
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
