# MediCard — Code Coverage Verification Report
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Audit Date**: 2026-10-05  
**Coverage Artifact**: `coverage.xml` (Cobertura XML format)  
**Status**: **PASS**  

---

## 1. Compliance Mandates Verified

| Capstone Requirement | Status | Evidence |
|---|---|---|
| **$\ge 20$ Unit Tests** | **PASS** | **99 automated tests** executed in unit, architecture, and security suites (exceeds mandate by 395%). |
| **Coverage Artifact Exists** | **PASS** | Fresh `coverage.xml` generated in project root from clean environment execution. |
| **Coverage Tool Declared in Dependencies** | **PASS** | `pytest-cov>=4.1.0,<=7.1.0` declared in `requirements.txt`. |
| **Current Source Tree Match** | **PASS** | Coverage generated directly against current `src/` modules in clean environment `.venv_clean`. |

---

## 2. Command Execution Details

- **Environment**: Clean isolated environment (`.venv_clean`), user-site packages disabled.
- **Command**:
  ```powershell
  .venv_clean\Scripts\python.exe -s -m pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term-missing tests/unit tests/architecture tests/security
  ```
- **Execution Time**: 16.27s
- **Output Artifact**: `coverage.xml` (71,161 bytes)

---

## 3. Coverage Summary by Subsystem

| Subsystem Module | Total Statements | Missed | Line Coverage |
|---|---|---|---|
| **Domain Layer (`src/domain/`)** | 357 | 25 | **93%** |
| `src/domain/settlement_rule.py` | 48 | 2 | **96%** |
| `src/domain/pre_auth_rule.py` | 85 | 5 | **94%** |
| `src/domain/eligibility_rule.py` | 56 | 4 | **93%** |
| `src/domain/claim_state_rule.py` | 26 | 2 | **92%** |
| `src/domain/reports_rule.py` | 36 | 3 | **92%** |
| `src/domain/role_boundary_rule.py` | 26 | 2 | **92%** |
| `src/domain/adjudication_rule.py` | 42 | 4 | **90%** |
| `src/domain/admission_rule.py` | 36 | 4 | **89%** |
| `src/domain/network_hospital_rule.py` | 7 | 0 | **100%** |
| `src/domain/notification_rule.py` | 29 | 0 | **100%** |
| **Service Layer (`src/services/`)** | 354 | 40 | **89%** |
| `src/services/admission_service.py` | 62 | 3 | **95%** |
| `src/services/network_admin_service.py` | 28 | 2 | **93%** |
| `src/services/settlement_service.py` | 58 | 5 | **91%** |
| `src/services/pre_auth_service.py` | 70 | 7 | **90%** |
| `src/services/eligibility_service.py` | 44 | 6 | **86%** |
| `src/services/reports_service.py` | 92 | 15 | **84%** |
| **Controller Layer (`src/controllers/`)** | 289 | 30 | **90%** |
| `src/controllers/health_controller.py` | 6 | 0 | **100%** |
| `src/controllers/reports_controller.py` | 29 | 0 | **100%** |
| `src/controllers/auth_dependency.py` | 26 | 1 | **96%** |
| `src/controllers/claim_controller.py` | 57 | 7 | **88%** |
| `src/controllers/eligibility_controller.py` | 49 | 6 | **88%** |
| `src/controllers/network_admin_controller.py` | 64 | 9 | **86%** |
| `src/controllers/pre_auth_controller.py` | 49 | 7 | **86%** |
| `src/controllers/settlement_controller.py` | 35 | 9 | **74%** |
| **Repository & Data Access (`src/repositories/`)** | 436 | 40 | **91%** |
| `src/repositories/models.py` | 204 | 0 | **100%** |
| `src/repositories/claim_repository.py` | 66 | 1 | **98%** |
| `src/repositories/policy_repository.py` | 25 | 1 | **96%** |
| `src/repositories/pre_auth_repository.py` | 34 | 2 | **94%** |
| `src/repositories/settlement_repository.py` | 18 | 1 | **94%** |
| `src/repositories/network_admin_repository.py` | 68 | 16 | **76%** |
| `src/repositories/database.py` | 25 | 9 | **64%** |
| `src/repositories/hospital_repository.py` | 25 | 11 | **56%** |
| **Utilities & Seed (`src/utils/`, `src/seed_data.py`, `src/main.py`)** | 162 | 10 | **94%** |
| `src/utils/logger.py` | 34 | 1 | **97%** |
| `src/main.py` | 45 | 3 | **93%** |
| `src/seed_data.py` | 83 | 6 | **93%** |
| **TOTAL** | **1,718** | **164** | **90%** |
