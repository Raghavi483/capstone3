# Sprint 3 Contract — Admission, Claim State Machine & Case Timeline
**Sprint**: Sprint 3  
**Target Acceptance Criteria**: AC-06, AC-08, AC-09  
**Associated Specifications**: `specs/admission_spec.md`, `specs/settlement_spec.md`  
**Primary Agent**: `state-machine-validator-agent.md`, `audit-tracer-agent.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-3-admission`  

---

## 1. Scope & Deliverables
1. **AC-06 Admission & Procedure Billing**:
   - Record patient admission date and procedure details (procedure name, code, cost).
   - Submit final bill with itemized summary.
   - Enforce buffer cap check: `bill_cap = pre_auth_amount * (1 + buffer_percentage)`.
2. **AC-08 Claim State Machine & Immutability**:
   - Enforce strict lifecycle: `PRE_AUTH` $\to$ `ADMITTED` $\to$ `DISCHARGED` $\to$ `SETTLED` / `DISPUTED` $\to$ `CLOSED`.
   - Illegal transitions raise `InvalidClaimStateException`.
   - Settled claim immutability: Settled claims cannot be modified.
3. **AC-09 Notifications & Timeline Transparency**:
   - Every state transition produces a stubbed notification for customer and hospital.
   - Case timeline endpoint provides complete chronological audit trail.

---

## 2. Invariants & Guardrails
- **State Machine Invariant**: Invalid transitions fail immediately with `InvalidClaimStateException`.
- **Immutability Invariant**: No post-settlement mutations permitted.
- **Decimal Invariant**: Pure Decimal for bill amounts.
- **Audit Logging**: Every transition logs to timeline and notification ledgers.
