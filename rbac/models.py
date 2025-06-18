from __future__ import annotations


class Permission:
    """Represents a permission in the RBAC system."""

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Permission) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"Permission({self.name!r})"


class Role:
    """Represents a role that can hold permissions and inherit from parent roles."""

    def __init__(self, name: str):
        self.name = name
        self.permissions: set[Permission] = set()
        self.parents: set[Role] = set()

    def add_permission(self, permission: Permission) -> None:
        """Adds a permission to the role."""
        self.permissions.add(permission)

    def add_parent(self, parent_role: Role) -> None:
        """Adds a parent role if it doesn't create a circular inheritance."""
        if self._creates_cycle(parent_role):
            raise ValueError(f"Adding {parent_role.name} as parent would create a cycle")
        self.parents.add(parent_role)

    def _creates_cycle(self, parent_role: Role) -> bool:
        """Detects cycle in the inheritance graph if this parent is added."""
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

    def get_all_permissions(self, visited=None) -> set[Permission]:
        """Recursively collects all permissions including inherited ones."""
        if visited is None:
            visited = set()
        if self in visited:
            return set()
        visited.add(self)

        perms = set(self.permissions)
        for parent in self.parents:
            perms |= parent.get_all_permissions(visited)
        return perms

    def __repr__(self) -> str:
        return f"Role({self.name!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Role) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class User:
    """Represents a user who may be assigned one or more roles."""

    def __init__(self, username: str):
        self.username = username
        self.roles: set[Role] = set()

    def add_role(self, role: Role) -> None:
        """Assigns a role to the user."""
        self.roles.add(role)

    def get_role_names(self) -> set[str]:
        """Returns the names of all roles assigned to the user."""
        return {role.name for role in self.roles}

    def get_all_permissions(self) -> set[Permission]:
        """Returns all permissions available to the user through assigned roles."""
        perms = set()
        for role in self.roles:
            perms |= role.get_all_permissions()
        return perms

    def has_permission(self, permission: Permission) -> bool:
        """Checks if the user has the given permission."""
        return permission in self.get_all_permissions()

    def __repr__(self) -> str:
        return f"User({self.username}, roles={[r.name for r in self.roles]})"


class Session:
    """
    Represents a user session that optionally activates a subset of roles.
    Useful for enforcing DSD (Dynamic Separation of Duty) constraints.
    """

    def __init__(self, user: User, active_roles: set[str]):
        self.user = user
        self.active_roles: set[str] = active_roles or set()

    def activate_role(self, role: str) -> None:
        """Activates a role if it's assigned to the user."""
        if role in self.user.get_role_names():
            self.active_roles.add(role)

    def __repr__(self) -> str:
        return f"Session(user={self.user.username!r})"
