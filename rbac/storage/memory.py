from typing import Optional
from rbac.storage.base import AbstractStorage
from rbac.models import User, Role, Permission

class InMemoryStorage(AbstractStorage):
    """
    In-memory implementation of the RBAC storage backend.
    Useful for testing and small-scale use cases.
    """

    def __init__(self):
        self.users: dict[str, User] = {}
        self.roles: dict[str, Role] = {}
        self.permissions: dict[str, Permission] = {}

    def save_user(self, user: User) -> None:
        """Save or update a user in memory."""
        self.users[user.username] = user

    def get_user(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        return self.users.get(username)

    def get_all_users(self) -> list[User]:
        """Return a list of all users."""
        return list(self.users.values())

    def save_role(self, role: Role) -> None:
        """Save or update a role in memory."""
        self.roles[role.name] = role

    def get_role(self, name: str) -> Optional[Role]:
        """Retrieve a role by name."""
        return self.roles.get(name)

    def get_all_roles(self) -> list[Role]:
        """Return a list of all roles."""
        return list(self.roles.values())

    def save_permission(self, permission: Permission) -> None:
        """Save or update a permission in memory."""
        self.permissions[permission.name] = permission

    def get_permission(self, name: str) -> Optional[Permission]:
        """Retrieve a permission by name."""
        return self.permissions.get(name)

    def get_all_permissions(self) -> list[Permission]:
        """Return a list of all permissions."""
        return list(self.permissions.values())

    def __repr__(self):
        return (
            f"<InMemoryStorage users={len(self.users)}, "
            f"roles={len(self.roles)}, permissions={len(self.permissions)}>"
        )
