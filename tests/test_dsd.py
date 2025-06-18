import pytest
from rbac.models import Role, User
from rbac.core.manager import RBACManager
from rbac.storage.memory import InMemoryStorage
from rbac.dsd.memory import InMemoryDSDConstraint


def test_dsd_violation():
    """Test session creation fails when activating conflicting roles."""
    dsd = InMemoryDSDConstraint(conflict_sets={
        "grading_restriction": {"exam_creator", "exam_grader"}
    })

    manager = RBACManager(storage=InMemoryStorage(), dsd_constraint=dsd)

    manager.add_role(Role("exam_creator"))
    manager.add_role(Role("exam_grader"))

    manager.add_user("alice")
    manager.assign_role("alice", "exam_creator")
    manager.assign_role("alice", "exam_grader")

    with pytest.raises(ValueError, match="DSD violation"):
        manager.create_session("alice", {"exam_creator", "exam_grader"})


def test_valid_session_with_one_of_conflicting_roles():
    """Test session creation succeeds with only one conflicting role."""
    dsd = InMemoryDSDConstraint(conflict_sets={
        "grading_restriction": {"exam_creator", "exam_grader"}
    })

    manager = RBACManager(storage=InMemoryStorage(), dsd_constraint=dsd)

    manager.add_role(Role("exam_creator"))
    manager.add_role(Role("exam_grader"))

    manager.add_user("bob")
    manager.assign_role("bob", "exam_creator")
    manager.assign_role("bob", "exam_grader")

    session = manager.create_session("bob", {"exam_creator"})
    assert session.user.username == "bob"
    assert session.active_roles == {"exam_creator"}


def test_updating_dsd_set_restricts_new_combinations():
    """Test that updating a DSD set with new roles enforces new restrictions."""
    dsd = InMemoryDSDConstraint()
    dsd.add_set("restricted", {"role1", "role2"})

    manager = RBACManager(storage=InMemoryStorage(), dsd_constraint=dsd)
    manager.add_role(Role("role1"))
    manager.add_role(Role("role2"))
    manager.add_user("john")
    manager.assign_role("john", "role1")
    manager.assign_role("john", "role2")

    with pytest.raises(ValueError, match="DSD violation"):
        manager.create_session("john", {"role1", "role2"})


def test_removal_of_dsd_set_allows_combination():
    """Test removing a DSD set allows sessions that were previously invalid."""
    dsd = InMemoryDSDConstraint(conflict_sets={
        "conflict": {"X", "Y"}
    })

    manager = RBACManager(storage=InMemoryStorage(), dsd_constraint=dsd)
    manager.add_role(Role("X"))
    manager.add_role(Role("Y"))
    manager.add_user("dave")
    manager.assign_role("dave", "X")
    manager.assign_role("dave", "Y")

    # Initially fails
    with pytest.raises(ValueError, match="DSD violation"):
        manager.create_session("dave", {"X", "Y"})

    # Remove the constraint and try again
    dsd.remove_set("conflict")
    session = manager.create_session("dave", {"X", "Y"})
    assert session.active_roles == {"X", "Y"}


def test_conflict_applies_only_to_active_roles():
    """Ensure conflicting roles can be assigned if not activated together."""
    dsd = InMemoryDSDConstraint(conflict_sets={
        "restricted": {"admin", "auditor"}
    })

    manager = RBACManager(storage=InMemoryStorage(), dsd_constraint=dsd)
    manager.add_role(Role("admin"))
    manager.add_role(Role("auditor"))

    manager.add_user("carol")
    manager.assign_role("carol", "admin")
    manager.assign_role("carol", "auditor")

    # Valid: only one active role
    session = manager.create_session("carol", {"admin"})
    assert session.active_roles == {"admin"}
