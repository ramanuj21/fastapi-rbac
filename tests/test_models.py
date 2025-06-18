from rbac.models import Role, Permission, User


def test_role_permission_assignment():
    """Test that a permission can be added to a role."""
    role = Role("admin")
    perm = Permission("delete")
    role.add_permission(perm)
    assert perm in role.permissions


def test_role_permission_deduplication():
    """Test that adding the same permission twice doesn't duplicate it."""
    role = Role("editor")
    perm = Permission("edit")
    role.add_permission(perm)
    role.add_permission(perm)
    assert list(role.permissions).count(perm) == 1


def test_role_inherits_permissions_from_parent():
    """Test that a role inherits permissions from its parent role."""
    parent = Role("reader")
    child = Role("writer")
    perm = Permission("read")

    parent.add_permission(perm)
    child.add_parent(parent)

    assert perm in child.get_all_permissions()


def test_multiple_parents_inherit_permissions():
    """Test that a role inherits permissions from multiple parents."""
    r1 = Role("viewer")
    r2 = Role("editor")
    child = Role("lead")

    p1 = Permission("view")
    p2 = Permission("edit")
    r1.add_permission(p1)
    r2.add_permission(p2)

    child.add_parent(r1)
    child.add_parent(r2)

    perms = child.get_all_permissions()
    assert p1 in perms and p2 in perms


def test_permission_propagation_to_user():
    """Test that a user inherits permissions from their assigned role."""
    role = Role("admin")
    perm = Permission("manage")
    role.add_permission(perm)

    user = User("alice")
    user.add_role(role)

    assert user.has_permission(perm)


def test_user_with_multiple_roles_gets_all_permissions():
    """Test that a user with multiple roles gets all role permissions."""
    reader = Role("reader")
    writer = Role("writer")
    read = Permission("read")
    write = Permission("write")

    reader.add_permission(read)
    writer.add_permission(write)

    user = User("bob")
    user.add_role(reader)
    user.add_role(writer)

    assert user.has_permission(read)
    assert user.has_permission(write)


def test_user_without_permission():
    """Test that a user without a permission returns False on check."""
    role = Role("guest")
    view = Permission("view")

    user = User("eve")
    user.add_role(role)

    assert not user.has_permission(view)


def test_deep_role_inheritance():
    """Test that deeply nested roles propagate permissions correctly."""
    a = Role("A")
    b = Role("B")
    c = Role("C")
    d = Role("D")
    p = Permission("deep")

    d.add_permission(p)
    c.add_parent(d)
    b.add_parent(c)
    a.add_parent(b)

    user = User("deep_user")
    user.add_role(a)

    assert user.has_permission(p)


def test_role_equality_and_hash():
    """Test that roles are equal by name and can be used in sets."""
    r1 = Role("auditor")
    r2 = Role("auditor")
    assert r1 == r2
    assert hash(r1) == hash(r2)
    assert len({r1, r2}) == 1


def test_permission_equality_and_hash():
    """Test that permissions are equal by name and usable in sets."""
    p1 = Permission("view")
    p2 = Permission("view")
    assert p1 == p2
    assert hash(p1) == hash(p2)
    assert len({p1, p2}) == 1


def test_role_inherits_duplicate_permissions_safely():
    """Test that a role does not duplicate inherited and direct permissions."""
    perm = Permission("update")
    parent = Role("base")
    child = Role("extended")

    parent.add_permission(perm)
    child.add_permission(perm)
    child.add_parent(parent)

    all_perms = child.get_all_permissions()
    assert list(all_perms).count(perm) == 1


def test_user_roles_and_string_representation():
    """Test user role assignment and user string output."""
    role = Role("admin")
    user = User("admin_user")
    user.add_role(role)

    assert role in user.roles
    assert "admin_user" in str(user)
