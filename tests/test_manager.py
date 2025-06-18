import pytest
from rbac.models import Role, Permission
from rbac.core.manager import RBACManager
from rbac.storage.memory import InMemoryStorage
from rbac.ssd.memory import InMemorySSDConstraint


# ─── USER CREATION AND DUPLICATES ─────────────────────────────────────────────

def test_add_user_and_duplicate():
    """Test user creation and handling of duplicate usernames."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("alice")
    with pytest.raises(ValueError):
        manager.add_user("alice")


# ─── ROLE CREATION AND DUPLICATES ─────────────────────────────────────────────

def test_add_role_and_duplicate():
    """Test role creation and rejection of duplicate role names."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_role(Role("admin"))
    with pytest.raises(ValueError):
        manager.add_role(Role("admin"))


# ─── PERMISSION CREATION AND DUPLICATES ───────────────────────────────────────

def test_add_permission_and_duplicate():
    """Test permission creation and duplicate check."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_permission("edit")
    with pytest.raises(ValueError):
        manager.add_permission("edit")


# ─── ROLE ASSIGNMENT ──────────────────────────────────────────────────────────

def test_assign_role_to_user():
    """Test assigning roles to users and verifying permission checks."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("alice")
    manager.add_role(Role("editor"))
    manager.add_permission("edit")

    manager.assign_role("alice", "editor")
    manager.grant_permission("editor", "edit")

    assert manager.user_has_permission("alice", "edit")


def test_assign_duplicate_role_is_idempotent():
    """Assigning the same role twice should not duplicate it."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("bob")
    manager.add_role(Role("user"))
    manager.assign_role("bob", "user")
    manager.assign_role("bob", "user")  # Idempotent

    user = manager.storage.get_user("bob")
    assert len(user.roles) == 1


# ─── PERMISSION CHECKS ────────────────────────────────────────────────────────

def test_user_does_not_have_permission():
    """User with no roles should not have any permissions."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("carol")
    assert not manager.user_has_permission("carol", "delete")


def test_permission_not_existing():
    """Permission check for non-existing permission should return False."""
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("carol")
    manager.add_role(Role("dev"))
    manager.assign_role("carol", "dev")
    assert not manager.user_has_permission("carol", "nonexistent")


# ─── ROLE HIERARCHY AND PERMISSION INHERITANCE ───────────────────────────────

def test_inherited_permissions_from_parent_role():
    """Permission from parent role should be inherited."""
    dev = Role("developer")
    admin = Role("admin")
    perm = Permission("deploy")
    dev.add_permission(perm)
    admin.add_parent(dev)

    manager = RBACManager(storage=InMemoryStorage())
    for role in [dev, admin]:
        manager.add_role(role)

    manager.add_user("dave")
    manager.assign_role("dave", "admin")
    assert manager.user_has_permission("dave", "deploy")


def test_deep_permission_inheritance():
    """Ensure permissions propagate through deep role hierarchies."""
    a = Role("A")
    b = Role("B")
    c = Role("C")
    d = Role("D")
    d.add_permission(Permission("deep"))

    c.add_parent(d)
    b.add_parent(c)
    a.add_parent(b)

    manager = RBACManager(storage=InMemoryStorage())
    for r in [a, b, c, d]:
        manager.add_role(r)
    manager.add_user("ellen")
    manager.assign_role("ellen", "A")

    assert manager.user_has_permission("ellen", "deep")


def test_role_inheritance_cycle_detection():
    """Role cannot inherit from itself or create a circular dependency."""
    a = Role("A")
    b = Role("B")
    c = Role("C")
    a.add_parent(b)
    b.add_parent(c)
    with pytest.raises(ValueError):
        c.add_parent(a)  # This would cause a cycle


# ─── SSD CONSTRAINTS ──────────────────────────────────────────────────────────

def test_ssd_violation_on_assignment():
    """SSD should block assignment of conflicting roles to same user."""
    ssd = InMemorySSDConstraint()
    ssd.add_set("conflict_set", {"editor", "reviewer"})

    manager = RBACManager(storage=InMemoryStorage(), ssd_constraint=ssd)
    manager.add_user("frank")
    manager.add_role(Role("editor"))
    manager.add_role(Role("reviewer"))

    manager.assign_role("frank", "editor")
    with pytest.raises(ValueError):
        manager.assign_role("frank", "reviewer")


def test_ssd_allows_non_conflicting_roles():
    """SSD should not block non-conflicting role combinations."""
    ssd = InMemorySSDConstraint()
    ssd.add_set("conflict_set", {"editor", "reviewer"})

    manager = RBACManager(storage=InMemoryStorage(), ssd_constraint=ssd)
    manager.add_user("grace")
    manager.add_role(Role("editor"))
    manager.add_role(Role("auditor"))

    manager.assign_role("grace", "editor")
    manager.assign_role("grace", "auditor")  # Not in conflict set


def test_ssd_multiple_conflict_sets_overlap():
    """SSD violation occurs even if the role overlaps two sets."""
    ssd = InMemorySSDConstraint()
    ssd.add_set("set1", {"A", "B"})
    ssd.add_set("set2", {"B", "C"})

    manager = RBACManager(storage=InMemoryStorage(), ssd_constraint=ssd)
    manager.add_user("harry")
    manager.add_role(Role("A"))
    manager.add_role(Role("B"))
    manager.add_role(Role("C"))

    manager.assign_role("harry", "A")
    manager.assign_role("harry", "C")

    with pytest.raises(ValueError):
        manager.assign_role("harry", "B")


def test_removal_of_ssd_set_allows_combination():
    """Removing SSD set should unblock previous violations."""
    ssd = InMemorySSDConstraint()
    ssd.add_set("no_mix", {"alpha", "beta"})

    manager = RBACManager(storage=InMemoryStorage(), ssd_constraint=ssd)
    manager.add_role(Role("alpha"))
    manager.add_role(Role("beta"))
    manager.add_user("irene")
    manager.assign_role("irene", "alpha")

    with pytest.raises(ValueError):
        manager.assign_role("irene", "beta")

    ssd.remove_set("no_mix")
    manager.assign_role("irene", "beta")  # Now allowed


# ─── LISTING ROLES AND PERMISSIONS ────────────────────────────────────────────

def test_get_all_role_names():
    """Test fetching all available roles from storage."""
    manager = RBACManager(storage=InMemoryStorage())
    for r in ["dev", "admin"]:
        manager.add_role(Role(r))
    assert set(role.name for role in manager.storage.get_all_roles()) == {"dev", "admin"}



def test_get_all_permission_names():
    """Test fetching all available permissions from storage."""
    manager = RBACManager(storage=InMemoryStorage())
    for p in ["read", "write"]:
        manager.add_permission(p)
    assert set(p.name for p in manager.storage.get_all_permissions()) == {"read", "write"}

