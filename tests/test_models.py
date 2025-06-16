# tests/test_models.py

from rbac.models import Permission, Role, User

def test_permission_assignment():
    upload = Permission("upload_homework")
    teacher = Role("teacher")
    teacher.add_permission(upload)
    
    assert upload in teacher.get_all_permissions()

def test_role_inheritance():
    upload = Permission("upload_homework")
    teacher = Role("teacher")
    teacher.add_permission(upload)

    admin = Role("admin")
    admin.add_parent(teacher)

    assert upload in admin.get_all_permissions()

def test_user_permissions():
    view = Permission("view_dashboard")
    editor = Role("editor")
    editor.add_permission(view)

    user = User("ramanuj")
    user.add_role(editor)

    assert user.has_permission(view)

def test_role_uniqueness():
    perm = Permission("export_report")
    role = Role("analyst")
    role.add_permission(perm)
    role.add_permission(perm)  # shouldn't duplicate

    assert len(role.permissions) == 1

def test_inherited_permission_from_parent_role():
    upload = Permission("upload_homework")
    teacher = Role("teacher")
    teacher.add_permission(upload)

    admin = Role("admin")
    admin.add_parent(teacher)

    alice = User("alice")
    alice.add_role(admin)

    assert alice.has_permission(upload)
