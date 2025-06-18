from pydantic import BaseModel, Field
from typing import Set, Dict

"""
Schemas related to session creation and response models.
"""


class SessionCreateRequest(BaseModel):
    """
    Request schema for creating a new session with selected active roles.
    """
    username: str = Field(..., description="Username for whom the session is being created", example="alice")
    active_roles: Set[str] = Field(
        ..., 
        description="Set of roles to activate in the session",
        example={"Editor", "Auditor"},
        min_length=1
    )


class SessionResponse(BaseModel):
    """
    Response schema after a session is successfully created.
    """
    username: str = Field(..., description="Username associated with the session", example="alice")
    active_roles: Set[str] = Field(..., description="Active roles in the session", example={"Editor", "Auditor"})
