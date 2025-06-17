import pytest
from rbac.manager import RBACManager
from rbac.models import User, Role, Permission
from rbac.storage import InMemoryStorage
from rbac.ssd.memory import InMemorySSDConstraint


@pytest.fixture
def rbac():
    return RBACManager(InMemoryStorage())

@pytest.fixture
def manager():
    return RBACManager(storage=InMemoryStorage())

def test_add_user_and_retrieve(rbac):
    rbac.add_user("alice")
    user = rbac.storage.get_user("alice")
    assert isinstance(user, User)
    assert user.username == "alice"


def test_add_role_and_permission(rbac):
    rbac.add_role(Role("teacher"))
    rbac.add_permission("edit_grades")

    role = rbac.storage.get_role("teacher")
    perm = rbac.storage.get_permission("edit_grades")

    assert isinstance(role, Role)
    assert isinstance(perm, Permission)


def test_assign_role_to_user(rbac):
    rbac.add_user("alice")
    rbac.add_role(Role("teacher"))
    rbac.assign_role("alice", "teacher")

    user = rbac.storage.get_user("alice")
    assert any(role.name == "teacher" for role in user.roles)


def test_grant_permission_to_role(rbac):
    rbac.add_role(Role("teacher"))
    rbac.add_permission("edit_grades")
    rbac.grant_permission("teacher", "edit_grades")

    role = rbac.storage.get_role("teacher")
    assert any(p.name == "edit_grades" for p in role.permissions)


def test_check_permission_true(rbac):
    rbac.add_user("alice")
    rbac.add_role(Role("teacher"))
    rbac.add_permission("edit_grades")

    rbac.assign_role("alice", "teacher")
    rbac.grant_permission("teacher", "edit_grades")

    assert rbac.check_permission("alice", "edit_grades") is True

def test_add_duplicate_user():
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("alice")

    with pytest.raises(ValueError, match="already exists"):
        manager.add_user("alice")


def test_add_duplicate_role():
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_role(Role("teacher"))

    with pytest.raises(ValueError, match="already exists"):
        manager.add_role(Role("teacher"))

def test_assign_role_to_unknown_user():
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_role(Role("admin"))

    with pytest.raises(ValueError, match="not found"):
        manager.assign_role("ghost", "admin")


def test_assign_unknown_role_to_user():
    manager = RBACManager(storage=InMemoryStorage())
    manager.add_user("alice")

    with pytest.raises(ValueError, match="not found"):
        manager.assign_role("alice", "nonexistent_role")

def test_add_duplicate_permission_to_role():
    role = Role("report_viewer")
    perm = Permission("view_reports")
    role.add_permission(perm)
    role.add_permission(perm)  # Should not raise, but should avoid duplication

    assert len(role.permissions) == 1

def test_check_permission_false(rbac):
    rbac.add_user("bob")
    rbac.add_role(Role("student"))
    rbac.add_permission("edit_grades")

    rbac.assign_role("bob", "student")

    assert rbac.check_permission("bob", "edit_grades") is False

def test_get_user_permissions():
    storage = InMemoryStorage()
    manager = RBACManager(storage=storage)

    role_viewer = Role("viewer")
    role_viewer.add_permission(Permission("view_grades"))

    role_editor = Role("editor")
    role_editor.add_permission(Permission("edit_grades"))

    manager.add_role(role_viewer)
    manager.add_role(role_editor)

    manager.add_user("bob")
    manager.assign_role("bob", "viewer")
    manager.assign_role("bob", "editor")

    permissions = manager.get_user_permissions("bob")
    assert permissions == {"view_grades", "edit_grades"}

def test_ssd_violation():
    ssd = InMemorySSDConstraint(conflict_sets={
    "exam_rules": {"exam_creator", "exam_grader"},
    "finance_rules": {"finance_admin", "audit_checker"}
})

    manager = RBACManager(storage=InMemoryStorage(), ssd_constraint=ssd)

    manager.add_role(Role("exam_creator"))
    manager.add_role(Role("exam_grader"))

    manager.add_user("alice")
    manager.assign_role("alice", "exam_creator")

    with pytest.raises(ValueError):
        manager.assign_role("alice", "exam_grader")


def test_role_inheritance_permissions():
    storage = InMemoryStorage()
    manager = RBACManager(storage)

    # Define roles
    student = Role("student")
    teacher = Role("teacher")
    admin = Role("admin")

    # Define permissions
    view_marks = Permission("view_marks")
    assign_grades = Permission("assign_grades")
    manage_users = Permission("manage_users")

    student.permissions.add(view_marks)
    teacher.permissions.add(assign_grades)
    admin.permissions.add(manage_users)

    # Set role hierarchy
    teacher.add_parent(student)  # teacher inherits student
    admin.add_parent(teacher)    # admin inherits teacher and student

    # Register roles and user
    manager.add_role(student)
    manager.add_role(teacher)
    manager.add_role(admin)

    user = manager.add_user("alice")
    user.add_role(admin)

    # Should inherit all 3 permissions
    assert manager.user_has_permission("alice", "view_marks")
    assert manager.user_has_permission("alice", "assign_grades")
    assert manager.user_has_permission("alice", "manage_users")




# ─── add_permission() error paths ───────────────────────────────────────────

def test_add_duplicate_permission(manager):
    # first creation succeeds
    manager.add_permission("export_reports")
    # second should raise ValueError
    with pytest.raises(ValueError, match="already exists"):
        manager.add_permission("export_reports")


# ─── grant_permission() error paths ──────────────────────────────────────────

def test_grant_permission_to_nonexistent_role(manager):
    # no roles created yet
    manager.add_permission("edit_marks")
    with pytest.raises(ValueError, match="Role 'nonrole' not found"):
        manager.grant_permission("nonrole", "edit_marks")

def test_grant_nonexistent_permission_to_role(manager):
    # role exists but permission does not
    manager.add_role(Role("teacher"))
    with pytest.raises(ValueError, match="Permission 'noperm' not found"):
        manager.grant_permission("teacher", "noperm")


# ─── check_permission() error paths ──────────────────────────────────────────

def test_check_permission_nonexistent_user(manager):
    # no users at all
    with pytest.raises(ValueError, match="User 'ghost' not found"):
        manager.check_permission("ghost", "anyperm")

def test_check_permission_nonexistent_permission(manager):
    # user exists but permission does not
    manager.add_user("alice")
    with pytest.raises(ValueError, match="Permission 'noperm' not found"):
        manager.check_permission("alice", "noperm")


# ─── user_has_permission() direct false path ─────────────────────────────────
# (assuming you have a user_has_permission method that returns False rather than raise)

def test_user_has_permission_not_found(manager):
    # if you choose to have a non-ValueError version:
    assert manager.user_has_permission("ghost", "anything") is False


# ─── role-hierarchy get_all_permissions and cycle protection ────────────────

def test_role_hierarchy_cycle_protection():
    r = Role("A")
    s = Role("B")
    t = Role("C")
    r.add_parent(s)
    s.add_parent(t)
    # adding A as parent of C should raise
    with pytest.raises(ValueError, match="cycle"):
        t.add_parent(r)

def test_get_all_permissions_visits_each_role_once():
    root = Role("root")
    child = Role("child")
    grand = Role("grand")

    p_root = Permission("p_root")
    p_child = Permission("p_child")
    p_grand = Permission("p_grand")

    root.add_permission(p_root)
    child.add_permission(p_child)
    grand.add_permission(p_grand)

    child.add_parent(root)
    grand.add_parent(child)

    # root -> child -> grand
    perms = {p.name for p in grand.get_all_permissions()}
    assert perms == {"p_root", "p_child", "p_grand"}


# ─── assign_role() SSD re-check (role names in visited_roles) ─────────────────

def test_ssd_conflict_detection_via_manager():
    from rbac.ssd.memory import InMemorySSDConstraint

    ssd = InMemorySSDConstraint()
    ssd.add_set("conflict1", {"R1", "R2"})

    m = RBACManager(storage=InMemoryStorage(), ssd_constraint=ssd)
    m.add_role(Role("R1"))
    m.add_role(Role("R2"))
    m.add_user("bob")
    m.assign_role("bob", "R1")

    with pytest.raises(ValueError, match="SSD violation"):
        m.assign_role("bob", "R2")

def test_collect_permissions_visited():
    a = Role("A")
    b = Role("B")
    c = Role("C")

    a.add_parent(b)
    a.add_parent(c)
    c.add_parent(b)  # B reachable via both A->B and A->C->B

    b.add_permission(Permission("read"))

    user = User("multi_path")
    user.add_role(a)

    manager = RBACManager(storage=InMemoryStorage())
    manager.storage.save_user(user)
    for role in [a, b, c]:
        manager.storage.save_role(role)

    # Should still get permission only once, and internally "visited_roles" will block second visit
    assert manager.user_has_permission("multi_path", "read")

def test_has_permission_cycle_detection_manual(caplog):
    r1 = Role("A")
    r2 = Role("B")
    r3 = Role("C")

    r1.parents.add(r2)
    r2.parents.add(r3)
    r3.parents.add(r1)  # cycle

    perm = Permission("cycle_test")
    r3.add_permission(perm)

    user = User("cycle_user")
    user.add_role(r1)

    manager = RBACManager(storage=InMemoryStorage())
    for role in (r1, r2, r3):
        manager.storage.save_role(role)
    manager.storage.save_user(user)

    with caplog.at_level("DEBUG"):
        has_perm = manager.user_has_permission("cycle_user", "cycle_test")

    assert not has_perm
    assert "Detected cycle in role inheritance" in caplog.text
