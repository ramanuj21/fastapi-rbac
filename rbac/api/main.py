from fastapi import APIRouter, HTTPException
from rbac.core import RBACManager
from rbac.storage import get_storage

# Schemas
from rbac.schemas.users import UserCreate, AssignRole, GetUserRolesResponse, RemoveUserRoleResponse
from rbac.schemas.roles import RoleCreateRequest, RoleListResponse, GrantPermission
from rbac.schemas.permissions import PermissionCreate, PermissionListResponse, CheckAccess, PermissionCheckRequest
from rbac.schemas.session import SessionCreateRequest, SessionResponse
from rbac.schemas.ssd import SSDCreateRequest, SSDListResponse
from rbac.schemas.dsd import DSDConflictSetRequest, DSDConflictSetUpdateRequest, DSDConflictSetsResponse

router = APIRouter()
rbac = RBACManager(storage=get_storage())

# --- User Management ---

@router.post("/users", summary="Create a new user", tags=["Users"])
def create_user(payload: UserCreate):
    """Creates a new user."""
    return rbac.add_user(payload.username)


@router.get("/users", response_model=list[str], summary="List all users", tags=["Users"])
def list_users():
    """Lists all registered users."""
    return [user.username for user in rbac.storage.get_all_users()]


@router.get("/users/{username}/roles", response_model=GetUserRolesResponse, tags=["Users"])
def get_user_roles(username: str):
    """Gets roles assigned to a user."""
    user = rbac.storage.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "roles": list(user.get_role_names())}


@router.delete("/users/{username}/roles/{role}", response_model=RemoveUserRoleResponse, tags=["Users"])
def remove_role_from_user(username: str, role: str):
    """Removes a role from a user."""
    user = rbac.storage.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.roles = {r for r in user.roles if r.name != role}
    rbac.storage.save_user(user)
    return {"username": username, "removed_role": role}

# --- Role Management ---

@router.post("/roles", summary="Create a new role", tags=["Roles"])
def create_role(data: RoleCreateRequest):
    """Creates a new role."""
    return rbac.add_role(data.to_role())


@router.get("/roles", response_model=RoleListResponse, tags=["Roles"])
def list_roles():
    """Lists all roles."""
    return {"roles": list(rbac.storage.get_all_role_names())}


@router.post("/assign-role", summary="Assign role to user", tags=["Roles"])
def assign_role(payload: AssignRole):
    """Assigns a role to a user."""
    rbac.assign_role(payload.username, payload.role)
    return {"status": "success"}


@router.post("/grant-permission", summary="Grant permission to a role", tags=["Roles"])
def grant_permission(payload: GrantPermission):
    """Grants a permission to a role."""
    rbac.grant_permission(payload.role, payload.permission)
    return {"status": "success"}

# --- Permission Management ---

@router.post("/permissions", summary="Create a new permission", tags=["Permissions"])
def create_permission(payload: PermissionCreate):
    """Creates a new permission."""
    return rbac.add_permission(payload.name)


@router.get("/permissions", response_model=PermissionListResponse, tags=["Permissions"])
def list_permissions():
    """Lists all permissions."""
    return {"permissions": list(rbac.storage.get_all_permission_names())}


@router.post("/check-permission", summary="Check user access", tags=["Permissions"])
def check_permission(payload: CheckAccess):
    """Checks if the user has a given permission."""
    try:
        result = rbac.check_permission(payload.username, payload.permission)
        return {"has_permission": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/check-permission-h", summary="Check user access (Hierarchical)", tags=["Permissions"])
def check_permission_h(data: PermissionCheckRequest):
    """Checks if user has a permission (hierarchical version)."""
    return {"has_permission": rbac.check_permission(data.username, data.permission)}

@router.get("/users/{username}/permissions", response_model=list[str], tags=["Permissions"])
def get_effective_permissions(username: str):
    """Lists all effective permissions for a user."""
    return list(rbac.get_user_permissions(username))

# --- SSD ---

@router.get("/ssd", response_model=SSDListResponse, tags=["SSD"])
def get_ssd_sets():
    """Retrieves all SSD (Static Separation of Duty) sets."""
    return {"sets": rbac.ssd.get_all_sets()}


@router.post("/ssd", summary="Create SSD conflict set", tags=["SSD"])
def create_ssd_conflicts(request: SSDCreateRequest):
    """Creates a new SSD conflict set."""
    rbac.ssd.add_set(request.name, set(request.roles))
    return {"status": "created"}


@router.delete("/ssd/{name}", summary="Delete SSD conflict set", tags=["SSD"])
def delete_ssd_set(name: str):
    """Deletes an SSD conflict set by name."""
    rbac.ssd.remove_set(name)
    return {"status": "deleted"}

# --- DSD ---

@router.get("/dsd", response_model=DSDConflictSetsResponse, tags=["DSD"])
def get_dsd_conflict_sets():
    """Retrieves all DSD (Dynamic Separation of Duty) conflict sets."""
    return {"conflict_sets": rbac.dsd.get_conflict_sets()}


@router.post("/dsd", summary="Add new DSD conflict set", tags=["DSD"])
def add_dsd_conflict_set(req: DSDConflictSetRequest):
    """Adds a new DSD conflict set."""
    rbac.dsd.add_set(req.name, req.roles)
    return {"status": "created"}


@router.put("/dsd/{set_name}", summary="Update DSD conflict set", tags=["DSD"])
def update_dsd_conflict_set(set_name: str, req: DSDConflictSetUpdateRequest):
    """Updates an existing DSD conflict set."""
    rbac.dsd.add_set(set_name, req.roles)
    return {"status": "updated"}


@router.delete("/dsd/{set_name}", summary="Delete DSD conflict set", tags=["DSD"])
def delete_dsd_conflict_set(set_name: str):
    """Deletes a DSD conflict set."""
    rbac.dsd.remove_set(set_name)
    return {"status": "deleted"}

# --- Session ---

@router.post("/sessions", response_model=SessionResponse, tags=["Sessions"])
def create_session(request: SessionCreateRequest):
    """Creates a user session with selected active roles."""
    session = rbac.create_session(request.username, request.active_roles)
    return SessionResponse(username=session.user.username, active_roles=session.active_roles)
