# FastAPI RBAC

A pluggable, extensible Role-Based Access Control (RBAC) system for FastAPI projects, supporting:
- Core RBAC with users, roles, and permissions
- Hierarchical role inheritance
- Static Separation of Duty (SSD)
- Dynamic Separation of Duty (DSD) with session-based constraints
- In-memory and pluggable storage backends
- FastAPI-friendly integration

---

## 📦 Features

- 🔐 **User, Role, Permission Management**
- 🧬 **Hierarchical Roles**
- ✅ **SSD & DSD constraint enforcement**
- 🧠 **Cycle detection in role inheritance**
- 🧪 **Pytest test suite with coverage**
- 🧱 **Pluggable Storage and Constraint Backends**

---

## 🚀 Getting Started

### 🐳 Docker (Recommended)

```bash
make build
make run
# Visit: http://localhost:9000/docs
🧪 Run Tests with Coverage

make test
# Coverage HTML will be in ./htmlcov/index.html

📂 Project Structure

rbac/
├── manager.py          # Core RBAC logic with SSD and DSD support
├── models.py           # User, Role, Permission, Session models
├── storage/            # Abstract and memory-based storage implementations
├── ssd/                # SSD base and in-memory implementation
├── dsd/                # DSD base and in-memory implementation
api/
├── main.py             # FastAPI app with endpoints (WIP)
tests/
├── ...                 # Unit tests

✍️ Example Usage

from rbac.manager import RBACManager
from rbac.models import Role, Permission
from rbac.storage.memory import InMemoryStorage

storage = InMemoryStorage()
rbac = RBACManager(storage)

rbac.add_user("alice")
rbac.add_role(Role("admin"))
rbac.add_permission("delete_resource")

rbac.assign_role("alice", "admin")
rbac.grant_permission("admin", "delete_resource")

assert rbac.check_permission("alice", "delete_resource")

📚 Documentation

See doc/architecture.md for internal design details.
📜 License

MIT License


---

### ✅ `doc/architecture.md`

```markdown
# Internal Architecture – FastAPI RBAC

This document outlines the internal design and extensibility of the FastAPI RBAC system.

---

## 🧱 Core Components

### 🧑‍💼 `User`
- Holds a list of assigned `Role` objects.
- Has helper methods like `add_role` and `has_permission`.

### 🛡️ `Role`
- Holds a list of `Permission` objects.
- Supports hierarchical inheritance using `.parents`.

### 🔐 `Permission`
- Represents a named access capability (e.g., `"read_post"`).

---

## 🧠 Role Hierarchy

Roles can inherit from other roles:

```text
admin
 └── manager
      └── viewer

This hierarchy allows permission inheritance up the chain.
Cycle detection is in place to prevent infinite loops.
⚖️ Constraints
✅ Static Separation of Duty (SSD)

    Prevents certain roles from being assigned together.

    Example: a user cannot be both "auditor" and "developer".

Implemented via:

class AbstractSSDConstraint:
    def is_valid_assignment(user: str, role: str, assigned_roles: set[str]) -> bool

🔁 Dynamic Separation of Duty (DSD)

    Prevents conflicting roles from being activated in the same session.

Implemented via:

class DSDConstraint:
    def is_valid_activation(active_roles: set[str]) -> bool

🧪 Session Model

Session-based permission checks use only active roles:

session = rbac.create_session("alice", {"manager", "viewer"})

This enforces DSD constraints at runtime.
🧰 Storage

All storage operations are abstracted via AbstractStorage.

Pluggable backends:

    InMemoryStorage (default)

    SQLAlchemyStorage (planned)

🧠 RBACManager Highlights
Public Methods

    add_user(username: str) → User

    add_role(role: Role) → Role

    add_permission(perm: str) → Permission

    assign_role(username: str, role_name: str)

    grant_permission(role_name: str, perm_name: str)

    check_permission(username: str, perm_name: str) → bool

    user_has_permission(username: str, permission_name: str) → bool

    get_user_permissions(username: str) → set[str]

    create_session(username: str, active_roles: set[str]) → Session

🌐 API Integration

Minimal FastAPI endpoints are defined in api/main.py. These can be extended with decorators for enforcement, e.g.:

@app.get("/secure-data")
def secure_data(user: str = Depends(get_user)):
    if not rbac.check_permission(user, "view_data"):
        raise HTTPException(status_code=403)

🔧 Planned Extensions

    SQLAlchemy-backed storage

    RESTful role/permission management endpoints

    FastAPI dependency injection decorators for permissions

    Multi-tenant support

    Audit logging

👥 Contributors

    @ramanuj21 – initial design & implementation


---
