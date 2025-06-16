import pytest
from rbac.manager import RBACManager
from rbac.models import User, Role, Permission
from rbac.storage import InMemoryStorage


@pytest.fixture
def rbac():
    return RBACManager(InMemoryStorage())


def test_add_user_and_retrieve(rbac):
    rbac.add_user("alice")
    user = rbac.storage.get_user("alice")
    assert isinstance(user, User)
    assert user.username == "alice"


def test_add_role_and_permission(rbac):
    rbac.add_role("teacher")
    rbac.add_permission("edit_grades")

    role = rbac.storage.get_role("teacher")
    perm = rbac.storage.get_permission("edit_grades")

    assert isinstance(role, Role)
    assert isinstance(perm, Permission)


def test_assign_role_to_user(rbac):
    rbac.add_user("alice")
    rbac.add_role("teacher")
    rbac.assign_role("alice", "teacher")

    user = rbac.storage.get_user("alice")
    assert any(role.name == "teacher" for role in user.roles)


def test_grant_permission_to_role(rbac):
    rbac.add_role("teacher")
    rbac.add_permission("edit_grades")
    rbac.grant_permission("teacher", "edit_grades")

    role = rbac.storage.get_role("teacher")
    assert any(p.name == "edit_grades" for p in role.permissions)


def test_check_permission_true(rbac):
    rbac.add_user("alice")
    rbac.add_role("teacher")
    rbac.add_permission("edit_grades")

    rbac.assign_role("alice", "teacher")
    rbac.grant_permission("teacher", "edit_grades")

    assert rbac.check_permission("alice", "edit_grades") is True


def test_check_permission_false(rbac):
    rbac.add_user("bob")
    rbac.add_role("student")
    rbac.add_permission("edit_grades")

    rbac.assign_role("bob", "student")

    assert rbac.check_permission("bob", "edit_grades") is False

