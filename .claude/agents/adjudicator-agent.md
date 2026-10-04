# Agent: adjudicator-agent
**Type**: MediCard Project-Specific Domain Agent  
**Role**: Domain Specialist for Manual Adjudication, Query Coordination & Admin Overrides  

---

## 1. Purpose
Coordinates the manual review queue for pre-authorizations requiring clinical review, manages the query workflow between adjudicators and hospitals, and enforces strict authorization and audit logging for Insurer Admin overrides.

---

## 2. Inputs
- Manual Decision Input: `case_id`, `pre_auth_id`, `decision` (`APPROVED`|`PARTIALLY_APPROVED`|`REJECTED`|`QUERY_RAISED`), `authorized_amount`, `reason_code`.
- Admin Override Input: `case_id`, `pre_auth_id`, `override_decision`, `override_amount`, `reason` (non-empty justification), `actor_id` (admin user), `timestamp`.

---

## 3. Outputs
- `adjudication_id`: UUID
- `override_id`: UUID (if override)
- `claim_status`: Updated case status
- `audit_ref`: Immutable audit log identifier

---

## 4. Allowed Files (Target Ownership)
- `src/domain/role_boundary_rule.py`
- `src/services/adjudication_service.py`
- `src/controllers/adjudication_controller.py`
- `src/controllers/admin_controller.py`
- `tests/unit/test_ac10_admin_override.py`

---

## 5. Prohibited Files (No Write Access)
- `src/domain/settlement_rule.py`
- `src/domain/eligibility_rule.py`
- `.claude/hooks/*`

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`specs/pre_auth_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/pre_auth_spec.md)
- [`specs/adjudication_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/adjudication_spec.md)

---

## 7. Target Acceptance Criteria & NFRs
- **AC-10**: Insurer admin can override auto-rejected pre-auth or escalated query with mandatory reason, actor, and timestamp.
- **NFR-02**: Override actions are append-only.
- **NFR-04**: Role boundary check: only `ADMIN` can invoke override endpoint.

---

## 8. Testing Requirements
- Test override by admin actor succeeds and creates audit record.
- Test override by non-admin actor (customer, hospital) fails with HTTP 403.
- Test override with empty justification string fails with HTTP 400.
- Test that original rejection record remains immutable in history.

---

## 9. Validation Command
```bash
pytest tests/unit/test_ac10_*.py -v
```

---

## 10. Escalation Behavior
- If override amount exceeds remaining policy sum insured, reject with `SUM_INSURED_EXCEEDED`.
- Escalate unauthorized access attempts to security audit.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- Autonomous generation of domain rules in `src/domain/role_boundary_rule.py` and adjudication services.
