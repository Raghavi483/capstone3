# Sprint 1 Contract: Eligibility & Network Hospital Administration
**Sprint**: Sprint 1  
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Target Branch**: `feat/sprint-1-eligibility`  
**Lead Agent**: `eligibility-agent`  
**Evaluator**: `evaluator` / Reviewer  
**Sprint Status**: IN_PROGRESS  

---

## 1. Sprint Objective
Implement customer registration, policy linking, coverage visibility (sum insured, exclusions, network hospitals), and real-time hospital eligibility lookup returning `ELIGIBLE` / `NOT_ELIGIBLE` with standardized reason codes.

---

## 2. In-Scope Acceptance Criteria & NFRs
- **AC-01**: Customer can register and link to their health policy. Coverage details visible (sum insured, exclusions, network hospitals).
- **AC-02**: Network hospital can look up customer eligibility by `member_id` and `policy_id`; returns `ELIGIBLE` or `NOT_ELIGIBLE` with reason codes.
- **NFR-01**: Fixed-point Decimal representation on all coverage balances.
- **NFR-04**: Role separation on API controllers (`CUSTOMER`, `HOSPITAL`).
- **NFR-07**: Health endpoint `/health` returning HTTP 200 within 1s.

---

## 3. Files Expected
- Domain:
  - `src/domain/eligibility_rule.py`
  - `src/domain/network_hospital_rule.py`
- Repositories & Database:
  - `src/repositories/database.py`
  - `src/repositories/models.py`
  - `src/repositories/policy_repository.py`
  - `src/repositories/hospital_repository.py`
- Services:
  - `src/services/eligibility_service.py`
- Controllers & Entry:
  - `src/controllers/eligibility_controller.py`
  - `src/controllers/health_controller.py`
  - `src/main.py`
- Seed Data:
  - `src/seed_data.py`
- Tests:
  - `tests/unit/test_ac01_policy_coverage.py`
  - `tests/unit/test_ac02_eligibility.py`
  - `tests/unit/test_nfr07_health.py`

---

## 4. TDD Red-Green Validation Criteria
- RED: Test files authored first; fail on missing modules.
- GREEN: Domain rules, repositories, and services generated; 100% tests pass.
- REFACTOR: Layer boundaries verified; 0 floating-point numbers in coverage fields.
- EVALUATION: Evaluator confirms AC-01 and AC-02 compliance.
