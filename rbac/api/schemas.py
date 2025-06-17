# rbac/api/schemas.py (add to existing file)
from pydantic import BaseModel

class SessionCreateRequest(BaseModel):
    username: str
    active_roles: set[str]

class SessionResponse(BaseModel):
    username: str
    active_roles: set[str]

class DSDConflictSetRequest(BaseModel):
    name: str
    roles: set[str]

class DSDConflictSetUpdateRequest(BaseModel):
    roles: set[str]

class DSDConflictSetsResponse(BaseModel):
    conflict_sets: dict[str, set[str]]

