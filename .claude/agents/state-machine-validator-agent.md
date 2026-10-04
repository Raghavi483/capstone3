# Agent: state-machine-validator-agent
**Type**: MediCard Project-Specific Technical Agent  
**Role**: Technical Specialist for Claim State Machine Progression & Lifecycle Integrity  

---

## 1. Purpose
Validates and enforces the cashless claim state transition graph:
`PRE_AUTH` $\to$ `ADMITTED` $\to$ `DISCHARGED` $\to$ `SETTLED` / `DISPUTED` $\to$ `CLOSED`.
Guarantees that out-of-order, illegal, or premature transitions immediately raise `InvalidClaimStateException`.

---

## 2. Inputs
- `case_id` (UUID string)
- `current_state` (string)
- `proposed_state` (string)
- `transition_context` (dictionary of preconditions: pre_auth_approved, bill_submitted, settlement_calculated)

---

## 3. Outputs
- `is_valid`: boolean
- `new_state`: string (if valid)
- `exception`: `InvalidClaimStateException` (if invalid)
- `transition_event`: Structured payload for notification dispatcher (AC-09)

---

## 4. Allowed Files (Target Ownership)
- `src/domain/claim_state_rule.py`
- `src/services/claim_lifecycle_service.py`
- `tests/unit/test_ac08_claim_state_machine.py`
- `tests/unit/test_ac09_notifications.py`

---

## 5. Prohibited Files (No Write Access)
- `src/domain/settlement_rule.py`
- `src/domain/eligibility_rule.py`
- `.claude/hooks/*`

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`specs/admission_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/admission_spec.md)

---

## 7. Target Acceptance Criteria
- **AC-08**: Cashless claim lifecycle progression; invalid transitions raise `InvalidClaimStateException`.
- **AC-09**: Every state transition generates a stubbed notification; case timeline queryable.

---

## 8. Testing Requirements
- Test happy path progression: `PRE_AUTH` $\to$ `ADMITTED` $\to$ `DISCHARGED` $\to$ `SETTLED` $\to$ `CLOSED`.
- Test alternate path: `DISCHARGED` $\to$ `DISPUTED` $\to$ `CLOSED`.
- Test all invalid transitions (e.g. `PRE_AUTH` $\to$ `SETTLED`, `ADMITTED` $\to$ `CLOSED`, `SETTLED` $\to$ `ADMITTED`) raising `InvalidClaimStateException`.
- Test timeline chronological ordering and stub notification dispatch.

---

## 9. Validation Command
```bash
pytest tests/unit/test_ac08_*.py tests/unit/test_ac09_*.py -v
```

---

## 10. Escalation Behavior
- If an unauthorized transition is attempted, raise `InvalidClaimStateException` with descriptive transition context and log a security warning.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- The agent must autonomously generate `src/domain/claim_state_rule.py` and state machine tests.
