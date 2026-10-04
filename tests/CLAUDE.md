# CLAUDE.md — Testing Directives (`tests/`)

## 1. Acceptance Criteria Mapping (Mandatory)
- Every single test file must explicitly reference its target AC ID in its file name or test docstrings:
  - `test_ac01_policy_coverage.py`
  - `test_ac02_eligibility.py`
  - `test_ac03_preauth_submission.py`
  - `test_ac04_preauth_lifecycle.py`
  - `test_ac05_auto_approval.py`
  - `test_ac06_bill_submission.py`
  - `test_ac07_settlement.py`
  - `test_ac08_claim_state_machine.py`
  - `test_ac09_notifications.py`
  - `test_ac10_admin_override.py`

## 2. Test Execution & Coverage
- Run all tests via:
  ```bash
  pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term-missing tests/
  ```
- All test suites must pass 100% with zero errors.
- Tests must use synthetic data only (**Rule 4**).

## 3. Architecture Tests (`tests/architecture/`)
- Must maintain at least 3 structural test suites:
  1. `test_layer_dependencies.py` — Verifies domain modules import zero controllers/services/frameworks.
  2. `test_phi_redaction.py` — Verifies logs never contain diagnostic terms.
  3. `test_append_only_rules.py` — Verifies audit and decision repositories lack update/delete operations.
