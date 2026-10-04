# Agent: settlement-agent
**Type**: MediCard Project-Specific Domain Agent  
**Role**: Domain Specialist for Final Bill Validation, Settlement Math & Payout Invariants  

---

## 1. Purpose
Executes the centralized financial settlement calculation for hospital cashless claims. Enforces policy buffer limits on final bills, deducts customer co-pays and deductibles, guarantees the non-negative payout invariant ($\ge 0$), and ensures append-only ledger storage.

---

## 2. Inputs
- `case_id` (UUID string)
- `final_bill` (Decimal): Total hospital invoice amount
- `pre_auth_amount` (Decimal): Authorized pre-authorization amount
- `buffer_percentage` (Decimal): Configured policy buffer ratio (e.g. `Decimal("0.10")` for 10%)
- `deductible` (Decimal): Patient deductible obligation
- `co_pay` (Decimal): Patient co-pay obligation

---

## 3. Outputs
- `settlement_id` (UUID string)
- `buffer_amount` (Decimal): `pre_auth_amount * buffer_percentage`
- `bill_cap` (Decimal): `pre_auth_amount + buffer_amount`
- `effective_bill` (Decimal): `min(final_bill, bill_cap)`
- `settlement_amount` (Decimal): `max(0, effective_bill - deductible - co_pay)`
- `patient_responsibility` (Decimal): `(final_bill - effective_bill) + deductible + co_pay`
- `settlement_status`: `SETTLED`

---

## 4. Allowed Files (Target Ownership)
- `src/domain/settlement_rule.py`
- `src/services/settlement_service.py`
- `src/controllers/settlement_controller.py`
- `src/repositories/settlement_repository.py`
- `tests/unit/test_ac06_bill_submission.py`
- `tests/unit/test_ac07_settlement.py`

---

## 5. Prohibited Files (No Write Access)
- `src/domain/pre_auth_rule.py`
- `src/domain/eligibility_rule.py`
- `src/domain/claim_state_rule.py`
- `.claude/hooks/*`

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`specs/admission_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/admission_spec.md)
- [`specs/settlement_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/settlement_spec.md)

---

## 7. Target Acceptance Criteria & NFRs
- **AC-06**: Final bill cannot exceed `pre_auth_amount + buffer_amount`.
- **AC-07**: Settlement amount = `min(final_bill, pre_auth_amount + buffer) - deductible - co_pay`; Invariant `settlement_amount >= 0`.
- **NFR-01**: All calculations use fixed-point `decimal.Decimal` (never floating-point).
- **NFR-02**: Settlements are append-only; historical records cannot be updated.

---

## 8. Testing Requirements
- Test bill equal to, less than, and greater than pre-auth amount.
- Test bill within buffer percentage vs exceeding buffer cap.
- Test high deductible/co-pay causing negative intermediate value $\to$ verified capped at zero.
- Test strict `TypeError` on float inputs.
- Test buffer percentage changes mid-cycle.

---

## 9. Validation Command
```bash
pytest tests/unit/test_ac06_*.py tests/unit/test_ac07_*.py -v
```

---

## 10. Escalation Behavior
- If `final_bill > pre_auth_amount + buffer_amount`, reject submission with `BILL_EXCEEDS_BUFFER_CAP` and transition claim to `DISPUTED`.
- If floating point is detected, trigger hook `settlement-cap-check` failure and halt build.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- The agent must autonomously generate the implementation of `src/domain/settlement_rule.py`.
- No hand-written mathematical shortcuts permitted.
