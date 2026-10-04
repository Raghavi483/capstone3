# CLAUDE.md — Repository Layer Directives (`src/repositories/`)

## 1. Append-Only Persistence (NFR-02, NFR-05)
- The repository layer provides data access via SQLAlchemy.
- **Append-Only Tables**:
  - `pre_auth_decisions`
  - `claim_bills`
  - `claim_settlements`
  - `audit_logs`
- These tables MUST NOT have physical `update()` or `delete()` methods in their repositories. All records are insert-only event representations.

## 2. In-Memory & SQLite Testability
- Must support both persistent file-based SQLite database and in-memory SQLite (`sqlite:///:memory:`) for high-speed test execution.
- Maintain schema migrations and versioned table mappings.
