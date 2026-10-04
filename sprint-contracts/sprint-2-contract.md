# Sprint 2 Contract — Pre-Authorization Engine & Adjudication Overrides
**Sprint**: Sprint 2  
**Target Acceptance Criteria**: AC-03, AC-04, AC-05, AC-10  
**Associated Specifications**: `specs/pre_auth_spec.md`, `specs/adjudication_spec.md`  
**Primary Agent**: `pre-auth-decider-agent.md`, `adjudicator-agent.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-2-preauth`  

---

## 1. Scope & Deliverables
1. **AC-03 Pre-Auth Submission**:
   - Hospital submits pre-authorization with `diagnosis`, `estimated_cost` (Decimal), `expected_admission_date`, `member_id`, `policy_id`, `hospital_id`.
   - Initial pre-authorization state must be `PENDING`.
2. **AC-04 Pre-Auth Decision Lifecycle**:
   - Transitions: `PENDING` $\to$ `APPROVED`, `PARTIALLY_APPROVED`, `REJECTED`, `QUERY_RAISED`.
   - Standardized reason codes required on all decisions.
   - Append-only decision ledger in `pre_auth_decisions`.
3. **AC-05 Auto-Approval Engine**:
   - Auto-approves when `estimated_cost <= 50000.00`, diagnosis is in approved whitelist, and `estimated_cost <= remaining_balance`.
   - Auto-rejects if diagnosis is excluded.
   - Partially approves if cost exceeds policy balance cap.
   - Raises query if procedure exceeds threshold or is unlisted.
4. **AC-10 Insurer Admin Override**:
   - Authorized role verification (`ADMIN` or `INSURER_ADMIN`).
   - Rejects unauthorized roles with 403 Forbidden.
   - Mandatory reason and actor audit record.
   - Invariant check: Approved amount cannot exceed policy remaining balance.

---

## 2. Invariants & Guardrails
- **Decimal Invariant**: Zero floating-point arithmetic for amounts.
- **Audit Invariant**: Append-only audit record created for every decision and override.
- **PHI Redaction**: Diagnosis redacted in operational logging.
- **Role Boundary**: Only `ADMIN` can execute overrides.
