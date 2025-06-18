# rbac/schemas/permissions.py
"""Schemas related to Permission operations."""

from pydantic import BaseModel, Field

class PermissionCreate(BaseModel):
    name: str = Field(..., description="Name of the permission to create", example="edit_article")

class CheckAccess(BaseModel):
    username: str = Field(..., description="Username to check access for", example="alice")
    permission: str = Field(..., description="Permission to check", example="edit_article")

class PermissionCheckRequest(BaseModel):
    username: str
    permission: str

class PermissionListResponse(BaseModel):
    permissions: list[str] = Field(..., description="List of all permission names")

class PermissionResponse(BaseModel):
    name: str
