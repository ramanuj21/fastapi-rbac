from .base import AbstractStorage
from .memory import InMemoryStorage

__all__ = ["AbstractStorage", "InMemoryStorage"]

def get_storage():
    return InMemoryStorage()

