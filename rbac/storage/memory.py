# rbac/storage/memory.py

from rbac.storage.base import AbstractStorage
from rbac.models import User, Role, Permission

class InMemoryStorage(AbstractStorage):
    def __init__(self):
        self.users = {}
        self.roles = {}
        self.permissions = {}

    def save_user(self, user: User) -> None:
        self.users[user.username] = user

    def get_user(self, username: str) -> User | None:
        return self.users.get(username)

    def save_role(self, role: Role) -> None:
        self.roles[role.name] = role

    def get_role(self, name: str) -> Role | None:
        return self.roles.get(name)

    def save_permission(self, permission: Permission) -> None:
        self.permissions[permission.name] = permission

    def get_permission(self, name: str) -> Permission | None:
        return self.permissions.get(name)
