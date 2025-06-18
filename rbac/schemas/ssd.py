"""Schemas related to Static Separation of Duty (SSD)."""
from pydantic import BaseModel, Field
from typing import List

class SSDSetCreate(BaseModel):
    name: str = Field(..., description="Name of the SSD constraint set")
    roles: List[str] = Field(..., description="List of roles that conflict statically")

class SSDCreateRequest(BaseModel):
    """
    Request model for creating an SSD conflict set.
    """
    name: str = Field(..., description="Unique name for the SSD conflict set", example="admin_exclusive")
    roles: List[str] = Field(
        ...,
        description="List of roles that should not be assigned together",
        example=["Admin", "Auditor"],
        min_length=2
    )

class SSDListResponse(BaseModel):
    """
    Response model listing all SSD conflict sets.
    """
    sets: dict[str, list[str]] = Field(
        ...,
        description="Dictionary of SSD conflict set names and their roles",
        example={"admin_exclusive": ["Admin", "Auditor"]}
    )

