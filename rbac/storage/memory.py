# rbac/storage/memory.py

from rbac.storage.base import AbstractStorage
from rbac.models import User, Role, Permission

class InMemoryStorage(AbstractStorage):
    def __init__(self):
        self.users: dict[str, User] = {}
        self.roles: dict[str, Role] = {}
        self.permissions: dict[str, Permission] = {}

    def save_user(self, user: User) -> None:
        self.users[user.username] = user

    def get_user(self, username: str) -> User | None:
        return self.users.get(username)
    
    def get_all_users(self) -> list[User]:
        return list(self.users.values())

    def save_role(self, role: Role) -> None:
        self.roles[role.name] = role

    def get_role(self, name: str) -> Role | None:
        return self.roles.get(name)

    def get_all_roles(self) -> list[Role]:
        return list(self.roles.values())

    def save_permission(self, permission: Permission) -> None:
        self.permissions[permission.name] = permission

    def get_permission(self, name: str) -> Permission | None:
        return self.permissions.get(name)
