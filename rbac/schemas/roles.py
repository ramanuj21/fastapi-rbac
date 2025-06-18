"""Schemas related to Role operations."""
from pydantic import BaseModel, Field
from typing import List
from rbac.models import Role

class RoleCreate(BaseModel):
    name: str = Field(..., description="Name of the role")

class RoleResponse(BaseModel):
    name: str
    permissions: List[str] = Field(default_factory=list)
    parents: List[str] = Field(default_factory=list)

class RoleListResponse(BaseModel):
    roles: list[str]

class GrantPermission(BaseModel):
    role: str = Field(..., description="Role name", example="Editor")
    permission: str = Field(..., description="Permission to grant", example="edit_article")

class RoleCreateRequest(BaseModel):
    """
    Request schema to create a new role.
    """
    name: str = Field(..., description="Name of the role to be created", example="Editor")
    parents: list[str] = Field(default_factory=list, description="Optional list of parent role names")

    def to_role(self) -> Role:
        return Role(self.name)
