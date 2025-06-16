# rbac/models.py

from __future__ import annotations
from typing import Set


class Permission:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Permission) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Permission({self.name!r})"


class Role:
    def __init__(self, name: str):
        self.name = name
        self.permissions: Set[Permission] = set()
        self.parents: Set[Role] = set()

    def add_permission(self, permission: Permission) -> None:
        self.permissions.add(permission)

    def get_all_permissions(self) -> Set[Permission]:
        """Return all permissions from this role and inherited parents"""
        perms = set(self.permissions)
        for parent in self.parents:
            perms |= parent.get_all_permissions()
        return perms

    def add_parent(self, parent_role: "Role"):
        if self._creates_cycle(parent_role):
            raise ValueError(f"Adding {parent_role.name} as parent would create a cycle")
        self.parents.add(parent_role)

    def _creates_cycle(self, parent_role: "Role") -> bool:
        """Check if adding the parent_role would create a circular inheritance."""
        visited = set()
        stack = [parent_role]
        while stack:
            role = stack.pop()
            if role == self:
                return True
            if role not in visited:
                visited.add(role)
                stack.extend(role.parents)
        return False


    def __repr__(self) -> str:
        return f"Role({self.name!r})"


class User:
    def __init__(self, username: str):
        self.username = username
        self.roles: Set["Role"] = set()

    def add_role(self, role: Role) -> None:
        self.roles.add(role)

    def get_all_permissions(self) -> Set[Permission]:
        perms = set()
        for role in self.roles:
            perms |= role.get_all_permissions()
        return perms

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.get_all_permissions()

    def __repr__(self) -> str:
        return f"User({self.username!r})"


class Session:
    """Optional session model to activate a subset of roles."""
    def __init__(self, user: User):
        self.user = user
        self.active_roles: Set[Role] = set()

    def activate_role(self, role: Role) -> None:
        if role in self.user.roles:
            self.active_roles.add(role)

    def get_active_permissions(self) -> Set[Permission]:
        perms = set()
        for role in self.active_roles:
            perms |= role.get_all_permissions()
        return perms

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.get_active_permissions()

    def __repr__(self) -> str:
        return f"Session(user={self.user.username!r})"

