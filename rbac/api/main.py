# rbac/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rbac.manager import RBACManager
from rbac.storage import InMemoryStorage

app = FastAPI(title="RBAC Demo API")
rbac = RBACManager(InMemoryStorage())

# Request Schemas
class UserCreate(BaseModel):
    username: str

class RoleCreate(BaseModel):
    name: str

class PermissionCreate(BaseModel):
    name: str

class AssignRole(BaseModel):
    username: str
    role: str

class GrantPermission(BaseModel):
    role: str
    permission: str

class CheckAccess(BaseModel):
    username: str
    permission: str


@app.post("/users")
def create_user(payload: UserCreate):
    try:
        user = rbac.add_user(payload.username)
        return {"msg": "User created", "username": user.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/roles")
def create_role(payload: RoleCreate):
    try:
        role = rbac.add_role(payload.name)
        return {"msg": "Role created", "role": role.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/permissions")
def create_permission(payload: PermissionCreate):
    try:
        perm = rbac.add_permission(payload.name)
        return {"msg": "Permission created", "permission": perm.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/assign-role")
def assign_role(payload: AssignRole):
    try:
        rbac.assign_role(payload.username, payload.role)
        return {"msg": f"Role '{payload.role}' assigned to user '{payload.username}'"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/grant-permission")
def grant_permission(payload: GrantPermission):
    try:
        rbac.grant_permission(payload.role, payload.permission)
        return {"msg": f"Permission '{payload.permission}' granted to role '{payload.role}'"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/check")
def check_permission(payload: CheckAccess):
    try:
        has_access = rbac.check_permission(payload.username, payload.permission)
        return {"access": has_access}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

