from fastapi import FastAPI
from rbac.api.main import router as rbac_router

app = FastAPI(
    title="RBAC API",
    version="1.0",
    description="A modular Role-Based Access Control system with SSD and DSD support.",
    openapi_tags=[
        {"name": "Users", "description": "Manage user accounts and their assigned roles."},
        {"name": "Roles", "description": "Create roles and assign them to users."},
        {"name": "Permissions", "description": "Manage permissions and assign them to roles."},
        {"name": "Access Control", "description": "Evaluate access and user permissions."},
        {"name": "SSD", "description": "Static Separation of Duty constraint management."},
        {"name": "DSD", "description": "Dynamic Separation of Duty constraint management."},
        {"name": "Sessions", "description": "Session-level role activation and validation."},
    ]
)

# Register the RBAC routes
app.include_router(rbac_router, prefix="/rbac")
