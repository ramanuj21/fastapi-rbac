from abc import ABC, abstractmethod
from typing import Optional
from rbac.models import Role, User, Permission

class AbstractStorage(ABC):
    """Abstract base class defining storage interface for RBAC entities."""

    @abstractmethod
    def save_user(self, user: User) -> None:
        """Persist or update a user in storage."""
        raise NotImplementedError("save_user must be implemented by subclass")

    @abstractmethod
    def get_user(self, username: str) -> Optional[User]:
        """Retrieve a user by username. Returns None if not found."""
        raise NotImplementedError("get_user must be implemented by subclass")

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """Return a list of all users."""
        raise NotImplementedError("get_all_users must be implemented by subclass")

    @abstractmethod
    def save_role(self, role: Role) -> None:
        """Persist or update a role in storage."""
        raise NotImplementedError("save_role must be implemented by subclass")

    @abstractmethod
    def get_role(self, name: str) -> Optional[Role]:
        """Retrieve a role by name. Returns None if not found."""
        raise NotImplementedError("get_role must be implemented by subclass")

    @abstractmethod
    def get_all_roles(self) -> list[Role]:
        """Return a list of all roles."""
        raise NotImplementedError("get_all_roles must be implemented by subclass")

    @abstractmethod
    def save_permission(self, permission: Permission) -> None:
        """Persist or update a permission in storage."""
        raise NotImplementedError("save_permission must be implemented by subclass")

    @abstractmethod
    def get_permission(self, name: str) -> Optional[Permission]:
        """Retrieve a permission by name. Returns None if not found."""
        raise NotImplementedError("get_permission must be implemented by subclass")

    @abstractmethod
    def get_all_permissions(self) -> list[Permission]:
        """Return a list of all permissions."""
        raise NotImplementedError("get_all_permissions must be implemented by subclass")
