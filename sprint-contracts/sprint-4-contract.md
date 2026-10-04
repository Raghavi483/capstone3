# Sprint 4 Contract — Settlement Calculator Engine (AC-07)
**Sprint**: Sprint 4  
**Target Acceptance Criteria**: AC-07, NFR-01, NFR-02  
**Associated Specifications**: `specs/settlement_spec.md` (v1.1.0)  
**Primary Agent**: `settlement-agent.md`, `audit-tracer-agent.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-4-settlement`  

---

## 1. Scope & Deliverables
1. **AC-07 Settlement Calculation Algorithm**:
   - `buffer_amount = (pre_auth_amount * buffer_percentage).quantize(Decimal("0.01"))`
   - `bill_cap = (pre_auth_amount + buffer_amount).quantize(Decimal("0.01"))`
   - `effective_bill = min(final_bill, bill_cap).quantize(Decimal("0.01"))`
   - `settlement_amount = max(Decimal("0.00"), effective_bill - deductible - co_pay).quantize(Decimal("0.01"))`
   - `patient_responsibility = ((final_bill - effective_bill) + deductible + co_pay).quantize(Decimal("0.01"))`
2. **10 Mandatory Edge Cases Tested**:
   1. Final bill strictly below buffer cap.
   2. Final bill exactly at buffer cap.
   3. Final bill strictly above buffer cap.
   4. Deductible application.
   5. Co-pay percentage/fixed application.
   6. Deductible + co-pay > effective bill (zero settlement invariant).
   7. Zero settlement scenario.
   8. Policy remaining balance cap interaction.
   9. Rounding / precision edge cases.
   10. Negative / invalid monetary inputs rejection.
3. **Settlement Persistence & Immutability**:
   - Append-only settlement record in `settlements` table.
   - Transitions claim status from `DISCHARGED` to `SETTLED`.
   - Once settled, claim is marked `is_settled=True` and cannot be modified.
   - Comprehensive audit trail entry.

---

## 2. Invariants & Guardrails
- **Floating Point Prohibition**: Absolute zero floating-point arithmetic.
- **Non-Negative Invariant**: `settlement_amount >= Decimal("0.00")`.
- **Identity Invariant**: `settlement_amount + patient_responsibility == final_bill` (when within policy cap).
