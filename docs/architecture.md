# 🔐 FastAPI RBAC Architecture

This document provides a technical overview of the RBAC (Role-Based Access Control) system designed for FastAPI. The system is modular, extensible, and aims to support real-world enterprise RBAC features such as SSD (Static Separation of Duty) and DSD (Dynamic Separation of Duty) constraints.

---

## 🧱 Core Components

### 1. `User`
- Represents an individual user.
- Can be assigned multiple `Role` instances.

### 2. `Role`
- Represents a collection of permissions.
- Can inherit from other roles (supports hierarchical RBAC).
- Prevents circular inheritance via cycle detection.

### 3. `Permission`
- Represents a named capability or action.
- Assigned to roles.

### 4. `Session`
- Represents a temporary session where a user activates a subset of their roles.
- Used for DSD validation.

---

## 🧠 Manager Layer (`RBACManager`)

The `RBACManager` is the main orchestrator that handles:
- Adding users, roles, and permissions.
- Assigning roles to users.
- Granting permissions to roles.
- Evaluating permissions using:
  - Hierarchical role traversal.
  - SSD and DSD constraints.
- Creating secure user sessions.

---

## 🗄️ Storage Abstraction

The system supports pluggable storage:

- `InMemoryStorage` (default)
- Future support: SQLAlchemy/PostgreSQL, Redis, etc.

All storage classes inherit from `AbstractStorage`.

---

## 🔐 SSD (Static Separation of Duty)

- Prevents conflicting roles from being **assigned** to the same user.
- Enforced during role assignment (`assign_role`).
- Pluggable via `AbstractSSDConstraint`.

Example:
> A user cannot hold both `FinanceManager` and `Auditor` roles simultaneously.

---

## 🔐 DSD (Dynamic Separation of Duty)

- Prevents conflicting roles from being **activated in a single session**.
- Enforced during session creation (`create_session`).
- Pluggable via `DSDConstraint` interface.

Example:
> A user *can be assigned* both `Developer` and `CodeReviewer`, but cannot activate both in one session.

---

## 🔁 Role Inheritance

- Roles can inherit from other roles.
- Permission checks are recursive with **cycle detection**.

---

## 🧪 Testing and Coverage

- Tests are written using `pytest`.
- Coverage checked with:
  ```bash
  pytest --cov=rbac --cov-report=html

    Makefile included to simplify building, running, and testing.

📂 Project Structure

rbac/
├── api/                  ← FastAPI integration layer (optional)
├── dsd/                  ← Dynamic Separation of Duty constraint system
├── manager.py            ← RBACManager logic
├── models.py             ← Data models for users, roles, permissions, sessions
├── ssd/                  ← Static Separation of Duty constraint system
├── storage/              ← Abstract and concrete storage backends
tests/                    ← Unit tests
doc/
└── architecture.md       ← This file

📦 Planned Features

SQLAlchemy-backed storage

FastAPI dependency-injection based permission decorators

Multi-tenant support

API for managing SSD/DSD constraints

    Caching layer for permissions

🧠 Design Philosophy

    Minimal but extensible core.

    Pluggable architecture.

    Clear separation between business logic and storage.

    Suited for microservices and monolithic apps alike.


