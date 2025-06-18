"""Schemas related to User operations."""
from pydantic import BaseModel, Field
from typing import List

class UserResponse(BaseModel):
    username: str
    roles: List[str] = Field(default_factory=list)

class RoleAssignment(BaseModel):
    username: str
    role_name: str

class UserCreate(BaseModel):
    username: str = Field(..., description="Username of the new user", example="alice")

class GetUserRolesResponse(BaseModel):
    username: str
    roles: list[str]

class RemoveUserRoleResponse(BaseModel):
    username: str
    removed_role: str

class AssignRole(BaseModel):
    """
    Request schema for assigning a role to a user.
    """
    username: str = Field(..., description="Username to assign the role to", example="alice")
    role: str = Field(..., description="Role to assign to the user", example="Editor")

