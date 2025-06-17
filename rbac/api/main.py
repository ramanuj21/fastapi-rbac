# rbac/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rbac.manager import RBACManager
from rbac.storage import InMemoryStorage
from rbac.models import Role, Permission


app = FastAPI(title="RBAC Demo API")
rbac = RBACManager(InMemoryStorage())

# Request Schemas
class UserCreate(BaseModel):
    username: str

class RoleCreateRequest(BaseModel):
    permissions: list[str] = []
    parents: list[str] = []
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

# Request schema
class PermissionCheckRequest(BaseModel):
    username: str
    permission: str

class SSDConflictSet(BaseModel):
    name: str
    roles: set[str]

class SSDCreateRequest(BaseModel):
    conflict_sets: list[SSDConflictSet]

@app.post("/rbac/has_permission", tags=["RBAC"])
def check_permission_h(data: PermissionCheckRequest):
    try:
        result = rbac.user_has_permission(data.username, data.permission)
        return {"username": data.username, "permission": data.permission, "has_permission": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users")
def create_user(payload: UserCreate):
    try:
        user = rbac.add_user(payload.username)
        return {"msg": "User created", "username": user.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/rbac/roles", tags=["RBAC"])
def create_role(data: RoleCreateRequest):
    role = Role(data.name)
    for perm in data.permissions:
        role.add_permission(Permission(perm))

    for parent_name in data.parents:
        print(rbac.storage.__dict__)
        parent_role = rbac.storage.get_role(parent_name)
        if not parent_role:
            raise HTTPException(status_code=400, detail=f"Parent role {parent_name} not found")
        role.add_parent(parent_role)

    rbac.add_role(role)
    return {"role": role.name, "permissions": data.permissions, "parents": data.parents}


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

@app.get("/users")
def list_users():
    return [user.username for user in rbac.storage.get_all_users()]

@app.get("/users/{username}/roles")
def get_user_roles(username: str):
    user = rbac.storage.get_user(username)
    return list(user.get_role_names())

@app.delete("/users/{username}/roles/{role}")
def remove_role_from_user(username: str, role: str):
    user = rbac.storage.get_user(username)
    user.roles = {r for r in user.roles if r.name != role}
    rbac.storage.save_user(user)
    return {"msg": f"Role '{role}' removed from user '{username}'"}

@app.get("/roles")
def list_roles():
    return list(rbac.storage.roles.keys())

@app.get("/permissions")
def list_permissions():
    return list(rbac.storage.permissions.keys())

@app.get("/users/{username}/permissions")
def get_effective_permissions(username: str):
    return list(rbac.get_user_permissions(username))

@app.get("/ssd")
def get_ssd_sets():
    return rbac.ssd.get_all_sets()  # returns {name: [roles...]}

@app.post("/ssd")
def create_ssd_conflicts(request: SSDCreateRequest):
    try:
        # Convert list of SSDConflictSet to internal format
        conflict_dict = {rbac.ssd.add_set(conf.name, conf.roles) for conf in request.conflict_sets}
        return {"status": "success", "conflict_sets": conflict_dict}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/ssd/{name}")
def delete_ssd_set(name: str):
    try:
        rbac.ssd.remove_set(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"msg": f"SSD set '{name}' deleted."}

