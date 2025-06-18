import pytest
from httpx import AsyncClient
from rbac.api.main import router
from fastapi import FastAPI

# Create test app instance
app = FastAPI()
app.include_router(router)

@pytest.mark.asyncio
async def test_full_rbac_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a user
        resp = await ac.post("/users", json={"username": "alice"})
        assert resp.status_code == 200
        assert resp.json() == {"username": "alice", "roles": []}


        # Create a role
        resp = await ac.post("/roles", json={"name": "teacher"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "teacher"

        # Create a permission
        resp = await ac.post("/permissions", json={"name": "edit_marks"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "edit_marks"

        # Assign role to user
        resp = await ac.post("/assign-role", json={"username": "alice", "role": "teacher"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

        # Grant permission to role
        resp = await ac.post("/grant-permission", json={"role": "teacher", "permission": "edit_marks"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

        # Check permission: should be True
        resp = await ac.post("/check-permission", json={"username": "alice", "permission": "edit_marks"})
        assert resp.status_code == 200
        assert resp.json()["has_permission"] is True

        # Negative test: unassigned user
        resp = await ac.post("/check-permission", json={"username": "bob", "permission": "edit_marks"})
        assert resp.status_code == 404  # "bob" doesn't exist
        assert resp.json()["detail"] == "User bob not found."
