# Agent: pre-auth-decider-agent
**Type**: MediCard Project-Specific Domain Agent  
**Role**: Domain Specialist for Pre-Authorization Intake, Decisioning & Auto-Approval  

---

## 1. Purpose
Evaluates hospital pre-authorization submissions against versioned policy terms, executes automated rule-based approvals up to policy caps for qualified clinical pathways, and routes edge cases to adjudicator queues.

---

## 2. Inputs
- `case_id` (UUID string)
- `member_id` (string)
- `policy_id` (string)
- `hospital_id` (string)
- `admission_diagnosis` (string)
- `estimated_cost` (Decimal)
- `expected_admission_date` (ISO-8601 date string)

---

## 3. Outputs
- `pre_auth_id` (UUID string)
- `status`: `PENDING` | `APPROVED` | `PARTIALLY_APPROVED` | `REJECTED` | `QUERY_RAISED`
- `authorized_amount`: Decimal
- `reason_code`: Standardized code (e.g. `AUTO_APPROVED_STANDARD_CARE`, `ESTIMATE_EXCEEDS_THRESHOLD`)
- `policy_version`: Policy rules version string

---

## 4. Allowed Files (Target Ownership)
- `src/domain/pre_auth_rule.py`
- `src/services/pre_auth_service.py`
- `src/controllers/pre_auth_controller.py`
- `src/repositories/pre_auth_repository.py`
- `tests/unit/test_ac03_preauth_submission.py`
- `tests/unit/test_ac04_preauth_lifecycle.py`
- `tests/unit/test_ac05_auto_approval.py`

---

## 5. Prohibited Files (No Write Access)
- `src/domain/settlement_rule.py`
- `src/domain/claim_state_rule.py`
- `src/controllers/admin_controller.py`
- `.claude/hooks/*`

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`specs/pre_auth_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/pre_auth_spec.md)
- [`specs/adjudication_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/adjudication_spec.md)

---

## 7. Target Acceptance Criteria
- **AC-03**: Hospital submits pre-auth entering initial `PENDING` state.
- **AC-04**: Pre-auth lifecycle progression with policy reason codes.
- **AC-05**: Auto-approval triggered if `estimated_cost <= threshold` AND `diagnosis in auto_approved_list`.

---

## 8. Testing Requirements
- Test auto-approval boundary conditions (`cost == threshold`, `cost = threshold - 0.01`, `cost = threshold + 0.01`).
- Test diagnosis matching (case-insensitive, exact whitelist).
- Test policy cap enforcement when estimate exceeds cap.
- Verify PHI redaction: diagnosis terms must not be passed to plaintext loggers (**NFR-03**).

---

## 9. Validation Command
```bash
pytest tests/unit/test_ac03_*.py tests/unit/test_ac04_*.py tests/unit/test_ac05_*.py -v
```

---

## 10. Escalation Behavior
- If diagnosis matches an exclusion list, reject immediately with `DIAGNOSIS_EXCLUDED`.
- If estimated cost exceeds threshold, escalate to `adjudicator-agent`.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- All production code in `src/domain/pre_auth_rule.py` and services must be generated autonomously.
