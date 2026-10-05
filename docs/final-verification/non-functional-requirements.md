# MediCard — Non-Functional Requirements Verification Report (NFR-01 through NFR-08)
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Audit Date**: 2026-10-05  
**Status**: ALL PASS  

Every Non-Functional Requirement (NFR-01 through NFR-08) has been audited and verified via automated AST checks, security boundary suites, isolated schema migration tests, or latency assertions.

---

### NFR-01: Zero Floating-Point Arithmetic (Decimal / Fixed-Point Only)
- **Requirement**: Money calculations, deductibles, copays, sum-insured, and settlements must strictly use Python `Decimal` or integer cents, never `float`.
- **Implementation**:
  - `src/domain/settlement_rule.py`, `src/domain/admission_rule.py`, `src/domain/pre_auth_rule.py`, `src/domain/eligibility_rule.py`
- **Enforcement & Tests**:
  - `tests/architecture/test_architecture_boundaries.py` (`test_arch_05_floating_point_prohibited_in_domain_rules`) uses Python AST to parse all domain modules and asserts zero `float` literals, zero `float()` type casts, and zero `float` annotations.
  - Domain tests (`test_ac01_sum_insured_float_rejection`, `test_ac03_submission_float_rejection`, `test_ac06_float_rejection`, `test_ac07_case_10_negative_or_invalid_monetary_input_rejection`) verify explicit rejection of float types with `TypeError`.
  - Static hook: `.claude/hooks/settlement-cap-check.ps1` scans for forbidden float syntax.
- **Command**:
  ```powershell
  python -m pytest tests/architecture/test_architecture_boundaries.py -k "floating_point" -v
  powershell -ExecutionPolicy Bypass -File .claude/hooks/settlement-cap-check.ps1
  ```
- **Result**: PASSED (0 float casts, 0 float literals, hook passed).
- **Status**: **PASS**

---

### NFR-02: Append-Only Immutability for Decisions, Bills, and Settlements
- **Requirement**: Pre-auth decisions, procedure records, discharge bills, settlements, and admin overrides are stored append-only. Settled claims cannot be modified.
- **Implementation**:
  - `src/repositories/models.py` (`PreAuthDecisionModel`, `ProcedureRecordModel`, `FinalBillModel`, `SettlementModel`, `AuditEventModel`)
  - `src/domain/claim_state_rule.py` (`transition_claim_state`)
- **Enforcement & Tests**:
  - `tests/unit/test_ac08_claim_state_machine.py:test_ac08_settled_claim_immutability` asserts that any attempt to transition or mutate a settled claim raises `InvalidClaimStateException`.
  - `tests/unit/test_ac04_pre_auth_lifecycle.py:test_ac04_invalid_transition_from_rejected` asserts rejection decisions are terminal and immutable.
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac08_claim_state_machine.py -k "settled_claim_immutability" -v
  ```
- **Result**: PASSED (Settled claims strictly immutable).
- **Status**: **PASS**

---

### NFR-03: PHI Protection and Redaction in Plaintext Logs
- **Requirement**: Protected Health Information (PHI) — including clinical diagnoses, procedure descriptions, treatment notes, and customer identifiers — must never appear unmasked in application logs.
- **Implementation**:
  - `src/utils/logger.py` (`mask_phi_in_data`, `StructuredJsonFormatter`)
- **Enforcement & Tests**:
  - `tests/unit/test_nfr03_phi_logging.py` (`test_nfr03_phi_redaction_masks_sensitive_medical_keys`) tests redaction of keys `diagnosis`, `procedure_description`, `clinical_notes`, `prescription`, `patient_name`, replacing sensitive values with `[REDACTED_PHI]`.
  - Static hook: `.claude/hooks/phi-redaction-check.ps1` scans production code for plaintext diagnosis prints.
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_nfr03_phi_logging.py -k "phi" -v
  powershell -ExecutionPolicy Bypass -File .claude/hooks/phi-redaction-check.ps1
  ```
- **Result**: PASSED (All PHI fields masked; hook passed).
- **Status**: **PASS**

---

### NFR-04: Controller Authentication & Role Boundaries
- **Requirement**: Controller-level authentication boundaries exist and enforce role isolation:
  - Unauthenticated requests receive HTTP 401.
  - Customers can access only their own coverage and claims.
  - Hospitals can access and submit claims only for their own hospital.
  - Insurer Admin overrides and network administration require ADMIN role; non-admins receive HTTP 403.
- **Implementation**:
  - `src/controllers/auth_dependency.py` (`require_role`, `verify_customer_access`, `verify_hospital_access`)
  - `src/controllers/pre_auth_controller.py`, `src/controllers/network_admin_controller.py`, `src/controllers/claim_controller.py`
- **Enforcement & Tests**:
  - `tests/security/test_controller_role_boundaries.py` (6 tests):
    - `test_unauthenticated_admin_override_returns_401`
    - `test_customer_attempting_admin_override_returns_403`
    - `test_hospital_attempting_network_onboarding_returns_403`
    - `test_customer_accessing_other_customer_coverage_returns_403`
    - `test_hospital_accessing_other_hospital_claim_returns_403`
    - `test_authorized_admin_override_succeeds_200`
  - `tests/security/test_role_boundaries.py` (7 domain role boundary tests).
  - Static hook: `.claude/hooks/role-boundary-check.ps1`.
- **Command**:
  ```powershell
  python -m pytest tests/security/test_controller_role_boundaries.py tests/security/test_role_boundaries.py -v
  powershell -ExecutionPolicy Bypass -File .claude/hooks/role-boundary-check.ps1
  ```
- **Result**: 13 passed in 1.48s; hook passed.
- **Status**: **PASS**

---

### NFR-05: Database & Policy Migrations Append-Only
- **Requirement**: Database schema built via append-only Alembic migrations; empty database can be migrated to `head` cleanly. Policy rules are versioned without mutating historical claim contracts.
- **Implementation**:
  - `alembic.ini`, `migrations/env.py`, `migrations/versions/1698a68ad50f_001_initial_schema.py`
  - `src/repositories/models.py` (`PolicyRuleVersionModel`)
- **Enforcement & Tests**:
  - `tests/unit/test_migrations.py:test_alembic_migrations_on_empty_database` runs Alembic migration against an empty SQLite file, brings it to `head`, asserts all 16 production entity tables are created, and verifies `alembic_version` table.
  - `tests/unit/test_policy_versioning.py:test_historical_claim_remains_bound_to_prior_policy_version` verifies historical claims retain original policy version rules when new versions are published.
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_migrations.py tests/unit/test_policy_versioning.py -v
  ```
- **Result**: 2 passed in 1.95s.
- **Status**: **PASS**

---

### NFR-06: Structured JSON Logging with Correlation ID & Case ID
- **Requirement**: Application logs emit structured JSON with timestamp, severity level, message, correlation ID, and claim/case ID.
- **Implementation**:
  - `src/utils/logger.py` (`StructuredJsonFormatter`, `get_logger`)
- **Enforcement & Tests**:
  - `tests/unit/test_nfr03_phi_logging.py:test_nfr03_structured_json_formatter_fields` validates JSON emission, checks presence of `correlation_id`, `case_id`, `timestamp`, `level`, and `logger`.
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_nfr03_phi_logging.py -k "structured" -v
  ```
- **Result**: PASSED.
- **Status**: **PASS**

---

### NFR-07: Health Endpoint Latency (< 1 Second SLA)
- **Requirement**: Unauthenticated `/health` endpoint returns HTTP 200 within 1,000 milliseconds of service boot.
- **Implementation**:
  - `src/controllers/health_controller.py` (`GET /health`)
- **Enforcement & Tests**:
  - `tests/unit/test_nfr07_health.py:test_nfr07_health_endpoint_status_and_latency` measures response latency and asserts status is 200 and latency is strictly < 1.0 second.
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_nfr07_health.py -v
  ```
- **Result**: 2 passed in 0.22s (Health endpoint latency measured at ~3.2ms, well within 1,000ms threshold).
- **Status**: **PASS**

---

### NFR-08: Architecture Structural Boundary AST Tests
- **Requirement**: Automated architectural tests verify strict Onion/layered boundaries:
  - Controllers must not import Repositories or Models.
  - Domain layer must have zero dependencies on web frameworks (`fastapi`, `starlette`) or ORM (`sqlalchemy`).
  - Repositories must not import Services or Controllers.
  - Services must not import Controllers.
- **Implementation**:
  - `tests/architecture/test_architecture_boundaries.py`
  - `.claude/hooks/architecture-boundary-check.ps1`
- **Enforcement & Tests**:
  - `test_arch_01_controllers_do_not_import_repositories_or_models`
  - `test_arch_02_domain_layer_strict_isolation`
  - `test_arch_03_repositories_do_not_import_services_or_controllers`
  - `test_arch_04_services_do_not_import_controllers`
  - `test_arch_05_floating_point_prohibited_in_domain_rules`
- **Command**:
  ```powershell
  python -m pytest tests/architecture/test_architecture_boundaries.py -v
  powershell -ExecutionPolicy Bypass -File .claude/hooks/architecture-boundary-check.ps1
  ```
- **Result**: 5 passed in 0.35s; hook passed.
- **Status**: **PASS**
