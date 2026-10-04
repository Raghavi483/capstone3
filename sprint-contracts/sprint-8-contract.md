# Sprint 8 Contract — Network Hospital & Coverage Administration (Priority 1)
**Sprint**: Sprint 8  
**Target Acceptance Criteria**: AC-NET-01, AC-NET-02, AC-NET-03, NET-01, NET-02, Section 4  
**Associated Specifications**: `specs/network_admin_spec.md`, `specs/app_spec.md`  
**Primary Agent**: `network-hospital-validator`, `architecture-test-agent`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-8-network-admin`  

---

## 1. Scope & Deliverables
1. **Network Hospital Administration (`src/domain/network_admin_rule.py`, `src/services/network_admin_service.py`)**:
   - Hospital onboarding: `hospital_id`, `hospital_name`, `tier` (`TIER_1`, `TIER_2`, `TIER_3`), `city`, `state`, `active_status`.
   - Hospital activation / deactivation toggle.
   - Filtering hospital directory by city and tier.
   - Enforce Rule NET-01: Only active hospitals recognized as in-network.
2. **Policy Product Configuration & Rule Sets (`src/domain/network_admin_rule.py`, `src/services/network_admin_service.py`)**:
   - Policy product configuration: `policy_code`, `product_name`, `default_sum_insured`, `auto_approval_threshold`, `buffer_percentage`, `auto_approved_diagnoses`, `exclusions`.
   - Validation: Reject negative auto-approval threshold, invalid tier, or empty identifiers.
3. **Repository & Persistence (`src/repositories/network_admin_repository.py`)**:
   - Persist hospitals, network hospital tiers, and policy configurations.
   - Append-only audit logging of all onboarding, status changes, and policy modifications to `audit_events`.
4. **API Controller (`src/controllers/network_admin_controller.py`)**:
   - `POST /api/v1/admin/hospitals/onboard` — Admin onboarding of network hospital.
   - `PATCH /api/v1/admin/hospitals/{hospital_id}/status` — Admin activation/deactivation toggle.
   - `GET /api/v1/admin/hospitals` — Queryable directory by city and tier.
   - `POST /api/v1/admin/policies/configure` — Policy product and threshold configuration.
   - `GET /api/v1/admin/policies/{policy_code}` — Retrieve policy configuration.
   - Role verification: `ADMIN` required; non-admin requests rejected with 403 Forbidden.
5. **Executable Tests (`tests/unit/test_ac_net_network_admin.py`)**:
   - Explicit tests referencing `AC-NET-01`, `AC-NET-02`, `AC-NET-03`.
   - Tests for admin authorization, non-admin rejection, tier filtering, negative threshold rejection, and audit recording.
6. **Frontend Integration (`frontend/index.html`, `frontend/app.js`)**:
   - Wire Network Admin tab to real backend endpoints.
