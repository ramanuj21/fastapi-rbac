# tests/test_storage.py

import pytest
from rbac.models import User, Role, Permission
from rbac.storage.memory import InMemoryStorage


def test_store_and_retrieve_user():
    """Test saving and retrieving a user."""
    store = InMemoryStorage()
    user = User("alice")
    store.save_user(user)

    fetched = store.get_user("alice")
    assert fetched is not None, "User not found"
    assert fetched.username == "alice", "Username mismatch"


def test_store_and_retrieve_role():
    """Test saving and retrieving a role."""
    store = InMemoryStorage()
    role = Role("teacher")
    store.save_role(role)

    fetched = store.get_role("teacher")
    assert fetched is not None, "Role not found"
    assert fetched.name == "teacher", "Role name mismatch"


def test_store_and_retrieve_permission():
    """Test saving and retrieving a permission."""
    store = InMemoryStorage()
    perm = Permission("upload_homework")
    store.save_permission(perm)

    fetched = store.get_permission("upload_homework")
    assert fetched is not None, "Permission not found"
    assert fetched.name == "upload_homework", "Permission name mismatch"


def test_user_has_permission_through_role():
    """Test user gets permission from assigned role."""
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
    assert fetched_user is not None, "User not retrieved"
    assert fetched_user.has_permission(perm), "Permission not propagated via role"


def test_role_inheritance_and_permission_resolution():
    """Test role inheritance and user permission resolution through ancestors."""
    store = InMemoryStorage()

    delete_user = Permission("delete_user")
    store.save_permission(delete_user)

    admin = Role("admin")
    staff = Role("staff")

    admin.add_permission(delete_user)
    staff.add_parent(admin)

    store.save_role(admin)
    store.save_role(staff)

    user = User("charlie")
    user.add_role(staff)
    store.save_user(user)

    fetched_user = store.get_user("charlie")
    assert fetched_user is not None, "User not found"
    assert fetched_user.has_permission(delete_user), "Permission not inherited through roles"


def test_detects_circular_role_inheritance():
    """Test that adding a parent which creates a cycle raises a ValueError."""
    store = InMemoryStorage()

    a = Role("A")
    b = Role("B")
    c = Role("C")

    a.add_parent(b)
    b.add_parent(c)

    with pytest.raises(ValueError, match="create a cycle"):
        c.add_parent(a)
