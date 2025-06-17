## ✅ RBAC Implementation Progress (NIST-aligned)

### Completed

- ✅ Core RBAC (Users, Roles, Permissions, Assignments)
- ✅ Hierarchical RBAC (Role inheritance, Cycle detection)
- ✅ Static Separation of Duty (SSD)
  - Constraint definition
  - Assignment enforcement
  - API support and tests
- ✅ In-memory storage backend
- ✅ FastAPI endpoints
- ✅ Test suite with coverage (~90%+)
- ✅ Dockerized setup using pyproject.toml

### Pending

- 🔁 Dynamic Separation of Duty (DSD)
  - Session-based role activation
  - DSD constraint management (API, validation, tests)
- 🧰 Optional Enhancements
  - Role/Permission revocation
  - List APIs (users, roles, permissions)
  - Persistent DB backend (SQLAlchemy)
  - Multi-tenant RBAC (for shaalaa.online)
  - Admin tools for import/export
