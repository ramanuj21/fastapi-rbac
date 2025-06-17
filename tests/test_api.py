# tests/test_api.py

import pytest
import pytest_asyncio

from httpx import AsyncClient
from rbac.api.main import app
from rbac.models import User, Role, Permission
from rbac.manager import RBACManager
from rbac.storage.memory import InMemoryStorage


@pytest.mark.asyncio
async def test_full_rbac_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a user
        resp = await ac.post("/users", json={"username": "alice"})
        assert resp.status_code == 200

        # Create a role
        resp = await ac.post("/rbac/roles", json={"name": "teacher"})
        assert resp.status_code == 200

        # Create a permission
        resp = await ac.post("/permissions", json={"name": "edit_marks"})
        assert resp.status_code == 200

        # Assign role to user
        resp = await ac.post("/assign-role", json={"username": "alice", "role": "teacher"})
        assert resp.status_code == 200

        # Grant permission to role
        resp = await ac.post("/grant-permission", json={"role": "teacher", "permission": "edit_marks"})
        assert resp.status_code == 200

        # Check permission: should be True
        resp = await ac.post("/check", json={"username": "alice", "permission": "edit_marks"})
        assert resp.status_code == 200
        assert resp.json()["access"] is True

        # Negative test: unassigned user
        resp = await ac.post("/check", json={"username": "bob", "permission": "edit_marks"})
        assert resp.status_code == 400  # bob doesn't exist
