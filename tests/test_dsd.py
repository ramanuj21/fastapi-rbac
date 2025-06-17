# tests/test_dsd.py
import pytest
from rbac.models import Role, User
from rbac.manager import RBACManager
from rbac.storage.memory import InMemoryStorage
from rbac.dsd.memory import InMemoryDSDConstraint

def test_dsd_violation():
    dsd = InMemoryDSDConstraint(conflict_sets={
        "grading_restriction": {"exam_creator", "exam_grader"}
    })

    manager = RBACManager(storage=InMemoryStorage(), dsd_constraint=dsd)

    manager.add_role(Role("exam_creator"))
    manager.add_role(Role("exam_grader"))

    manager.add_user("alice")
    manager.assign_role("alice", "exam_creator")
    manager.assign_role("alice", "exam_grader")

    # Should raise a violation because both roles are in the same conflict set
    with pytest.raises(ValueError, match="DSD violation"):
        manager.create_session("alice", {"exam_creator", "exam_grader"})

def test_valid_session():
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
    assert "exam_creator" in session.active_roles
