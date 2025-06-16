# rbac/storage/base.py

from abc import ABC, abstractmethod
from rbac.models import Role, User, Permission

class AbstractStorage(ABC):
    @abstractmethod
    def save_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, username: str) -> User | None:
        pass

    @abstractmethod
    def save_role(self, role: Role) -> None:
        pass

    @abstractmethod
    def get_role(self, name: str) -> Role | None:
        pass

    @abstractmethod
    def save_permission(self, permission: Permission) -> None:
        pass

    @abstractmethod
    def get_permission(self, name: str) -> Permission | None:
        pass
