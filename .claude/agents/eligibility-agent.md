# Agent: eligibility-agent
**Type**: MediCard Project-Specific Domain Agent  
**Role**: Domain Specialist for Member Registration, Coverage Visibility & Hospital Eligibility Resolution  

---

## 1. Purpose
Evaluates customer health policy coverage, validates member eligibility lookups conducted by network hospitals, enforces active term and network participation rules, and returns standardized reason codes.

---

## 2. Inputs
- `member_id` (string): Unique identifier of policyholder.
- `policy_id` (string): Unique policy contract reference.
- `hospital_id` (string): Facility identifier of the querying hospital.
- `lookup_date` (ISO-8601 date string): Intake date.

---

## 3. Outputs
- `status`: `ELIGIBLE` | `NOT_ELIGIBLE`
- `available_balance`: Decimal (Remaining sum insured)
- `exclusions`: Array of excluded conditions
- `reason_codes`: Standardized codes (`POL_INACTIVE`, `HOSP_OUT_OF_NETWORK`, `SUM_INSURED_EXHAUSTED`, `POL_NOT_FOUND`)
- `policy_version`: Policy rules version string

---

## 4. Allowed Files (Target Ownership)
- `src/domain/eligibility_rule.py`
- `src/domain/network_hospital_rule.py`
- `src/services/eligibility_service.py`
- `src/controllers/eligibility_controller.py`
- `tests/unit/test_ac01_policy_coverage.py`
- `tests/unit/test_ac02_eligibility.py`

---

## 5. Prohibited Files (No Write Access)
- `src/domain/settlement_rule.py`
- `src/domain/pre_auth_rule.py`
- `src/domain/claim_state_rule.py`
- `src/repositories/audit_repository.py`
- `.claude/hooks/*`
- Root infrastructure and CI configuration files

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`specs/eligibility_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/eligibility_spec.md)
- [`specs/network_admin_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/network_admin_spec.md)

---

## 7. Target Acceptance Criteria
- **AC-01**: Customer registration, policy linking, coverage visibility (sum insured, exclusions, network hospitals).
- **AC-02**: Hospital eligibility lookup returning `ELIGIBLE` or `NOT_ELIGIBLE` with standardized reason codes.

---

## 8. Testing Requirements
- TDD Red-Green-Refactor discipline mandatory.
- Author unit tests covering:
  - Active policy with sufficient balance and network hospital $\to$ `ELIGIBLE`.
  - Out-of-network hospital $\to$ `NOT_ELIGIBLE` with `HOSP_OUT_OF_NETWORK`.
  - Exhausted sum insured $\to$ `NOT_ELIGIBLE` with `SUM_INSURED_EXHAUSTED`.
  - Expired policy date $\to$ `NOT_ELIGIBLE` with `POL_INACTIVE`.
  - Decimal monetary precision on all balance amounts.

---

## 9. Validation Command
```bash
pytest tests/unit/test_ac01_*.py tests/unit/test_ac02_*.py -v
```

---

## 10. Escalation Behavior
- If policy rules are ambiguous or conflicting, escalate to Lead Orchestrator; update `specs/eligibility_spec.md` before proceeding.
- If hospital network status is disputed, route to Admin governance.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- The agent must generate implementation code strictly via autonomous generation tasks.
- No direct manual edits by human engineers to `src/` or `tests/`.
