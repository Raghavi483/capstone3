# Remediation & Implementation Execution Plan
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Document**: `docs/remediation-plan.md`  
**Purpose**: Sequential, phased roadmap for moving all scaffolded and missing capstone requirements to full verified compliance while adhering to Rule 1 (No-Hand-Coding) and Rule 3 (PR-Driven Development).

---

## Phase Overview

```
PHASE 0: Foundation Correction (Substrate, Harness Plugin, SDK, Spec Disambiguation)
  ↓
PHASE 1: Architecture Blueprint & TDD Blueprint Verification
  ↓
PHASE 2: Eligibility & Network Hospital Administration (AC-01, AC-02) [PR #2]
  ↓
PHASE 3: Pre-Authorization Submission, Auto-Approval & Override (AC-03, AC-04, AC-05, AC-10) [PR #3]
  ↓
PHASE 4: Admission Tracking, Procedure Records & State Machine (AC-06, AC-08, AC-09) [PR #4]
  ↓
PHASE 5: Settlement Calculator, Buffer Enforcement & Audit Ledger (AC-07, NFR-01, NFR-02) [PR #4]
  ↓
PHASE 6: Multi-Party Responsive UI (Customer, Hospital, Adjudicator, Admin) [PR #5]
  ↓
PHASE 7: Playwright E2E Testing, Snapshots & Architecture Tests (NFR-08) [PR #5]
  ↓
PHASE 8: CI/CD Pipeline & Coverage Artifacts (`coverage.xml`)
  ↓
PHASE 9: PR-Driven Git History & Audit Trail Verification (≥ 3 PR Merges)
  ↓
PHASE 10: Final 100-Mark Rubric Evaluation Gate
```

---

## Phase Breakdown & Phase Contracts

### PHASE 0 — Foundation Correction
- **Objective**: Repair AI-native foundation, install real Claude Harness Engine plugin, integrate real Anthropic SDK, and eliminate specification ambiguities.
- **Agent Responsible**: Lead Orchestrator
- **Specification**: All specifications (`specs/*.md`), [`docs/spec-issues.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/spec-issues.md)
- **Target ACs**: Foundation, NFR-01, NFR-03, NFR-04
- **Files Expected**: `C:\Users\Admin\claude-harness-engine`, `~/.claude/settings.json`, `scripts/run_feature_agent.py`, `specs/settlement_spec.md` (v1.1.0)
- **Tests Expected**: Hook validations, SDK verification (`python scripts/run_feature_agent.py --verify-sdk`)
- **Validation Command**:
  ```bash
  powershell -ExecutionPolicy Bypass -File .claude/hooks/phi-redaction-check.ps1
  powershell -ExecutionPolicy Bypass -File .claude/hooks/settlement-cap-check.ps1
  python scripts/run_feature_agent.py --verify-sdk
  ```
- **Evidence Expected**: Audit logs, clean hook passes, `docs/capstone-compliance-matrix.md`.
- **Status**: COMPLETE.

---

### PHASE 1 — Architecture & TDD Blueprint Verification
- **Objective**: Establish and verify the layered architectural contracts and TDD red-green-refactor workflows.
- **Agent Responsible**: `architecture-test-agent` + `planner`
- **Specification**: [`docs/architecture.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/architecture.md), [`docs/tdd.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/tdd.md)
- **Target ACs**: NFR-08, Section 7.3
- **Files Expected**: `docs/architecture.md`, `docs/tdd.md`, `tests/architecture/conftest.py`
- **Tests Expected**: Preliminary architecture structure test scaffolding
- **Validation Command**: `pytest tests/architecture/ -v`
- **Evidence Expected**: Document sign-off in `sprint-contracts/`

---

### PHASE 2 — Eligibility Engine & Network Hospital Admin (PR #2)
- **Objective**: Implement customer registration, policy linking, coverage benefits, and hospital eligibility lookup.
- **Branch**: `feat/sprint-2-eligibility`
- **Agent Responsible**: `eligibility-agent` + `test-engineer`
- **Specification**: [`specs/eligibility_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/eligibility_spec.md), [`specs/network_admin_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/network_admin_spec.md)
- **Target ACs**: **AC-01, AC-02, NFR-04, NFR-07**
- **Files Expected**:
  - `src/domain/eligibility_rule.py`
  - `src/domain/network_hospital_rule.py`
  - `src/services/eligibility_service.py`
  - `src/repositories/policy_repository.py`
  - `src/controllers/eligibility_controller.py`
- **Tests Expected**:
  - `tests/unit/test_ac01_policy_coverage.py` (Coverage visibility, sum insured)
  - `tests/unit/test_ac02_eligibility.py` (ELIGIBLE vs NOT_ELIGIBLE with reason codes)
- **Validation Command**: `pytest tests/unit/test_ac01_*.py tests/unit/test_ac02_*.py -v`
- **Evidence Expected**: PR #2 merge commit via `--no-ff`, evaluator review log in `specs/reviews/`.

---

### PHASE 3 — Pre-Authorization Engine & Adjudicator Override (PR #3)
- **Objective**: Implement pre-authorization intake, auto-approval rule evaluation, decision lifecycle, and audited admin override.
- **Branch**: `feat/sprint-3-preauth`
- **Agent Responsible**: `pre-auth-decider-agent` + `adjudicator-agent`
- **Specification**: [`specs/pre_auth_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/pre_auth_spec.md), [`specs/adjudication_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/adjudication_spec.md)
- **Target ACs**: **AC-03, AC-04, AC-05, AC-10**
- **Files Expected**:
  - `src/domain/pre_auth_rule.py`
  - `src/domain/role_boundary_rule.py`
  - `src/services/pre_auth_service.py`
  - `src/services/adjudication_service.py`
  - `src/controllers/pre_auth_controller.py`
  - `src/controllers/admin_controller.py`
- **Tests Expected**:
  - `tests/unit/test_ac03_preauth_submission.py`
  - `tests/unit/test_ac04_preauth_lifecycle.py`
  - `tests/unit/test_ac05_auto_approval.py`
  - `tests/unit/test_ac10_admin_override.py`
- **Validation Command**: `pytest tests/unit/test_ac03_*.py tests/unit/test_ac04_*.py tests/unit/test_ac05_*.py tests/unit/test_ac10_*.py -v`
- **Evidence Expected**: PR #3 merge commit via `--no-ff`, override audit log evidence.

---

### PHASE 4 — Admission Tracking & Claim State Machine (PR #4 Part 1)
- **Objective**: Implement hospital intake tracking, procedure records, final bill submission with buffer limits, and rigid state machine.
- **Branch**: `feat/sprint-4-5-settlement`
- **Agent Responsible**: `state-machine-validator-agent` + `test-engineer`
- **Specification**: [`specs/admission_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/admission_spec.md)
- **Target ACs**: **AC-06, AC-08, AC-09**
- **Files Expected**:
  - `src/domain/claim_state_rule.py`
  - `src/services/admission_service.py`
  - `src/services/notification_service.py`
  - `src/controllers/admission_controller.py`
- **Tests Expected**:
  - `tests/unit/test_ac06_bill_submission.py`
  - `tests/unit/test_ac08_claim_state_machine.py`
  - `tests/unit/test_ac09_notifications.py`
- **Validation Command**: `pytest tests/unit/test_ac06_*.py tests/unit/test_ac08_*.py tests/unit/test_ac09_*.py -v`
- **Evidence Expected**: State transition logs, timeline query verification.

---

### PHASE 5 — Settlement Calculator & Append-Only Audit (PR #4 Part 2)
- **Objective**: Implement fixed-point decimal settlement calculation, buffer capping, deductible/co-pay subtraction, zero-floor invariant, and append-only ledger.
- **Branch**: `feat/sprint-4-5-settlement`
- **Agent Responsible**: `settlement-agent` + `audit-tracer-agent`
- **Specification**: [`specs/settlement_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/settlement_spec.md) (v1.1.0)
- **Target ACs**: **AC-07, NFR-01, NFR-02**
- **Files Expected**:
  - `src/domain/settlement_rule.py`
  - `src/services/settlement_service.py`
  - `src/repositories/settlement_repository.py`
  - `src/repositories/audit_repository.py`
  - `src/controllers/settlement_controller.py`
- **Tests Expected**:
  - `tests/unit/test_ac07_settlement.py` (Edge cases: zero bill, high deductible, buffer overflow, float rejection)
- **Validation Command**:
  ```bash
  pytest tests/unit/test_ac07_*.py -v
  powershell -ExecutionPolicy Bypass -File .claude/hooks/settlement-cap-check.ps1
  ```
- **Evidence Expected**: PR #4 merge commit via `--no-ff`, settlement invariant test trace.

---

### PHASE 6 — Multi-Party Responsive Frontend (PR #5 Part 1)
- **Objective**: Implement responsive, accessible web portals for Customer, Hospital, Adjudicator, and Admin with deterministic test IDs.
- **Branch**: `feat/sprint-6-7-frontend-arch`
- **Agent Responsible**: `ui-designer` + `design-critic`
- **Specification**: [`frontend/CLAUDE.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/frontend/CLAUDE.md), User Journeys in [`docs/business-case.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/business-case.md)
- **Target ACs**: Customer Portal, Hospital Desk, Adjudicator Workbench, Admin View
- **Files Expected**:
  - `frontend/index.html`
  - `frontend/css/styles.css`
  - `frontend/js/app.js`
  - `frontend/js/api.js`
- **Tests Expected**: UI component DOM validation
- **Validation Command**: Browser manual/automated check
- **Evidence Expected**: Responsive layout screenshots, working client interface.

---

### PHASE 7 — Playwright E2E Tests, Snapshots & Architecture Tests (PR #5 Part 2)
- **Objective**: Implement automated browser validation via Playwright MCP with snapshot directory, and author 3 AST structural tests.
- **Branch**: `feat/sprint-6-7-frontend-arch`
- **Agent Responsible**: `architecture-test-agent` + `evaluator`
- **Specification**: [`tests/CLAUDE.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/tests/CLAUDE.md), [`docs/architecture.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/architecture.md)
- **Target ACs**: **NFR-03, NFR-06, NFR-08**
- **Files Expected**:
  - `tests/e2e/test_cashless_journey.py`
  - `tests/e2e/snapshots/`
  - `tests/architecture/test_layer_dependencies.py`
  - `tests/architecture/test_phi_redaction.py`
  - `tests/architecture/test_append_only_rules.py`
- **Tests Expected**: At least 3 architecture structural tests and Playwright E2E journey.
- **Validation Command**:
  ```bash
  pytest tests/architecture/ -v
  pytest tests/e2e/ -v
  ```
- **Evidence Expected**: PR #5 merge commit via `--no-ff`, Playwright snapshot files.

---

### PHASE 8 — CI/CD Pipeline & Coverage Artifacts
- **Objective**: Execute full test suite, verify 100% pass, generate Cobertura `coverage.xml`, and validate GitLab CI integration.
- **Agent Responsible**: Lead Orchestrator
- **Specification**: [`.gitlab-ci.yml`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/.gitlab-ci.yml)
- **Target ACs**: CI/CD (6 marks), Coverage Artifact
- **Files Expected**: `coverage.xml`, `.gitlab-ci.yml`
- **Tests Expected**: Cumulative 20+ unit tests, architecture tests, E2E tests.
- **Validation Command**:
  ```bash
  pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term-missing tests/
  ```
- **Evidence Expected**: Generated and committed `coverage.xml`, passing CI pipeline test.

---

### PHASE 9 — PR-Driven Git History & Audit Trail Verification
- **Objective**: Audit final git topology to verify at least 3 PR-driven non-fast-forward merges, complete sprint contracts, post-mortems, and knowledge deposits.
- **Agent Responsible**: Lead Orchestrator
- **Specification**: [`docs/git-compliance.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/git-compliance.md), [`docs/knowledge-deposits.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/knowledge-deposits.md)
- **Target ACs**: Rubric Category 5
- **Files Expected**: `docs/post-mortems/`, `docs/fix-loops/`, `specs/reviews/`
- **Validation Command**: `git log --graph --oneline`
- **Evidence Expected**: At least 3 `Merge pull request #...` commits with full non-fast-forward topology.

---

### PHASE 10 — Final Rubric Evaluation Gate (100 Marks)
- **Objective**: Conduct comprehensive scoring across all 21 parameters of the AI-Native Engineering Rubric.
- **Agent Responsible**: `evaluator` + Lead Orchestrator
- **Target Score**: $\ge 90$ (Distinction)
- **Evidence Expected**: Final assessment report and complete evidence package.
