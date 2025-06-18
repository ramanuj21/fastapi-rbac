"""Schemas related to Dynamic Separation of Duty (DSD)."""
from pydantic import BaseModel, Field

class DSDSetCreate(BaseModel):
    name: str = Field(..., description="Name of the DSD constraint set")
    roles: set[str] = Field(..., description="List of roles that cannot be active together")

class DSDConflictSetRequest(BaseModel):
    """
    Request schema to define a new DSD conflict set.
    """
    name: str = Field(..., description="Unique name of the conflict rule", example="editorial_conflict")
    roles: set[str] = Field(
        ..., 
        description="Set of roles that should not be active together",
        example={"Editor", "Publisher"},
        min_length=2
    )


class DSDConflictSetUpdateRequest(BaseModel):
    """
    Request schema to update roles in an existing DSD conflict set.
    """
    roles: set[str] = Field(
        ..., 
        description="Updated set of conflicting roles",
        example={"Editor", "Reviewer"},
        min_length=2
    )


class DSDConflictSetsResponse(BaseModel):
    """
    Response schema for listing all current DSD conflict sets.
    """
    conflict_sets: dict[str, set[str]] = Field(
        ...,
        description="Mapping of conflict set names to sets of conflicting roles",
        example={
            "editorial_conflict": {"Editor", "Publisher"},
            "audit_conflict": {"Auditor", "FinanceAdmin"}
        }
    )
