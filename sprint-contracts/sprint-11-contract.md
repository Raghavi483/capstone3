# Sprint 11 Contract — Controller-Level Role & Authentication Boundary (Priority 4)
**Sprint**: Sprint 11  
**Target Acceptance Criteria**: Section 8, NFR-04, Controller Role Boundaries  
**Associated Specifications**: `specs/app_spec.md`, `specs/adjudication_spec.md`, `CLAUDE.md`  
**Primary Agent**: `security-reviewer.md`, `test-engineer.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-11-controller-authorization`  

---

## 1. Scope & Deliverables
1. **Controller Authentication & Authorization Module (`src/controllers/auth_dependency.py`)**:
   - Parse authentication context from request headers (`X-User-Id`, `X-User-Role`, `X-Hospital-Id`, `X-Member-Id`).
   - Rejects unauthenticated admin/sensitive operations with HTTP 401 Unauthorized.
   - Enforces role access boundaries:
     - `CUSTOMER`: restricted to own member ID data and coverage; cannot perform hospital or admin actions (HTTP 403 Forbidden).
     - `HOSPITAL`: restricted to own facility (`X-Hospital-Id`); cross-hospital operations rejected with HTTP 403 Forbidden.
     - `INSURER`: can review pre-auths, claims, and operational analytics.
     - `ADMIN`: authorized for elevated overrides, network onboarding, and configuration mutations.
   - Disallows insecure fallback defaults (`default="ADMIN"` strictly removed).
2. **Controller Integration**:
   - `src/controllers/pre_auth_controller.py`: Require authenticated ADMIN for `/admin/preauth/override` without default header.
   - `src/controllers/claim_controller.py`: Validate hospital tenancy on admission and discharge.
   - `src/controllers/eligibility_controller.py`: Restrict customer coverage lookups to matching member ID.
3. **Executable Security Tests (`tests/security/test_controller_role_boundaries.py`)**:
   - `test_unauthenticated_admin_override_returns_401`
   - `test_customer_accessing_other_customer_coverage_returns_403`
   - `test_hospital_accessing_other_hospital_claim_returns_403`
   - `test_customer_attempting_admin_override_returns_403`
   - `test_hospital_attempting_network_onboarding_returns_403`
   - `test_authorized_admin_override_succeeds_200`
