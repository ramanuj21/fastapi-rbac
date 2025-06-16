# tests/test_storage.py

from rbac.models import User, Role, Permission
from rbac.storage.memory import InMemoryStorage

def test_store_and_retrieve_user():
    store = InMemoryStorage()
    user = User("alice")
    store.save_user(user)

    fetched = store.get_user("alice")
    assert fetched is not None
    assert fetched.username == "alice"

def test_store_and_retrieve_role():
    store = InMemoryStorage()
    role = Role("teacher")
    store.save_role(role)

    fetched = store.get_role("teacher")
    assert fetched is not None
    assert fetched.name == "teacher"

def test_store_and_retrieve_permission():
    store = InMemoryStorage()
    perm = Permission("upload_homework")
    store.save_permission(perm)

    fetched = store.get_permission("upload_homework")
    assert fetched is not None
    assert fetched.name == "upload_homework"

def test_user_has_permission_through_role():
    store = InMemoryStorage()

    perm = Permission("grade_homework")
    store.save_permission(perm)

    role = Role("teacher")
    role.add_permission(perm)
    store.save_role(role)

    user = User("bob")
    user.add_role(role)
    store.save_user(user)

    fetched_user = store.get_user("bob")
    assert fetched_user is not None
    assert fetched_user.has_permission(perm)

def test_role_inheritance_and_permission_resolution():
    store = InMemoryStorage()

    # Create a permission
    delete_user = Permission("delete_user")
    store.save_permission(delete_user)

    # Create roles
    admin = Role("admin")
    staff = Role("staff")

    # Assign permission to admin
    admin.add_permission(delete_user)

    # Make staff inherit from admin
    staff.add_parent(admin)

    store.save_role(admin)
    store.save_role(staff)

    # Create user and assign 'staff' role (which inherits 'admin')
    user = User("charlie")
    user.add_role(staff)
    store.save_user(user)

    # Fetch user and test permission resolution
    fetched_user = store.get_user("charlie")
    assert fetched_user is not None
    assert fetched_user.has_permission(delete_user)

import pytest

def test_detects_circular_role_inheritance():
    store = InMemoryStorage()

    a = Role("A")
    b = Role("B")
    c = Role("C")

    a.add_parent(b)
    b.add_parent(c)

    # Try to make C a parent of A — should raise error
    with pytest.raises(ValueError, match="create a cycle"):
        c.add_parent(a)

