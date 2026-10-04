# Sprint 5 Contract — Architecture Tests, Role Security & Coverage (NFR-01, NFR-08, Section 8, Section 15, Section 16)
**Sprint**: Sprint 5  
**Target Acceptance Criteria**: NFR-01, NFR-08, Sections 8, 15, 16  
**Associated Specifications**: `specs/app_spec.md`, `CLAUDE.md`  
**Primary Agent**: `architecture-test-agent.md`, `security-reviewer.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-5-architecture-security`  

---

## 1. Scope & Deliverables
1. **Architecture AST Invariant Tests (`tests/architecture/test_architecture_boundaries.py`)**:
   - `test_controllers_do_not_import_repositories`: Controllers only import services, domain entities/exceptions.
   - `test_domain_layer_isolation`: Domain code has zero dependencies on services, controllers, or repositories.
   - `test_repositories_do_not_import_services_or_controllers`: Repositories do not depend on upper layers.
   - `test_services_do_not_import_controllers`: Services do not depend on presentation controllers.
   - `test_no_float_usage_in_domain`: Scans domain layer AST for float literals or `float()` calls.
2. **Security & Role Boundary Enforcement (`src/domain/role_boundary_rule.py`, `tests/security/test_role_boundaries.py`)**:
   - Multi-tenant tenant boundary checks for `CUSTOMER`, `HOSPITAL`, `INSURER`, `ADMIN`.
   - Rejection of cross-hospital or cross-customer resource access.
   - Admin-only override permissions.
3. **Formal Test Coverage Metric**:
   - Configuration of `pytest-cov`.
   - Generation of executable `coverage.xml`.
   - Verification of >= 80% coverage on core business logic.

---

## 2. Invariants & Guardrails
- **Structural Clean Architecture**: Strict one-way inward dependency.
- **Pure Decimal**: Zero floating-point arithmetic allowed in monetary domains.
- **Multi-Tenant Isolation**: Hospital A can never access Hospital B's patient claim data.
