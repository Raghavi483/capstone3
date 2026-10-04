# MediCard Platform Root Specification (app_spec)
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform  
**Business Case ID**: BC-AINE-017  
**Specification Level**: System Root Architecture & Common Invariants  
**Version**: 1.0.0  

---

## 1. Purpose
This root specification defines the overarching system architecture, domain boundary standards, data schemas, role authentication constraints, state transition machines, and non-functional guarantees governing all MediCard platform components.

---

## 2. Actors & Role Hierarchy
- **CUSTOMER**: Authenticated individual policyholder holding a MediCard membership. Can view personal policies, sum insured, exclusions, network hospitals, claim timelines, and post-discharge summaries.
- **HOSPITAL**: Authorized network healthcare provider staff. Can perform member eligibility lookup, submit pre-authorizations, record patient admissions, submit procedure records and final bills. Restricted strictly to cases initiated at their hospital facility (**NFR-04**).
- **INSURER**: Adjudication and claims management officers. Can review pre-authorization queues, raise clinical queries, approve/partially approve/reject claims, and inspect operational metrics.
- **ADMIN**: Insurer system administrators possessing elevated governance privileges. Can execute pre-authorization overrides with mandatory justifications, manage network hospitals, and configure versioned coverage rules.

---

## 3. Global Inputs & Shared Schemas
- `MemberID`: Unique alphanumeric string identifying the policyholder (e.g. `MEM-100234`).
- `PolicyID`: Unique alphanumeric string identifying the active insurance policy (e.g. `POL-550912`).
- `HospitalID`: Unique alphanumeric string identifying the network healthcare provider (e.g. `HOSP-001`).
- `CaseID`: System-generated UUID identifying the claim lifecycle journey.
- `CorrelationID`: UUID propagating across all logs and HTTP headers for end-to-end distributed tracing.

---

## 4. Global Outputs
- Standardized REST JSON payloads.
- Structured JSON logs (**NFR-06**).
- Append-only audit records containing `case_id`, `actor_id`, `action`, `timestamp`, `justification`, and `previous_state` (**NFR-02**).

---

## 5. Domain Rules & Core Invariants
- **NFR-01 (Fixed-Point Decimal)**: All currency amounts (sums insured, estimated costs, pre-auth approvals, final bills, deductibles, co-pays, settlements) MUST be computed in Python `decimal.Decimal` with 2 decimal places. Floating-point arithmetic is prohibited across all domain calculation paths.
- **NFR-02 & NFR-05 (Append-Only Persistence)**: Pre-authorization decisions, bill submissions, settlements, and administrative overrides are strictly append-only. No physical `UPDATE` or `DELETE` operations on historical ledger entries.
- **NFR-03 (PHI Redaction)**: Patient Protected Health Information (PHI) including clinical diagnoses, procedure descriptions, and medical history MUST NEVER appear in plaintext application logs. Logs must reference tokenized Case IDs.
- **NFR-04 (Role & Tenant Boundary)**: Endpoint authorization MUST enforce role checks at the controller boundary. A hospital user can never access or query claims belonging to other hospitals.
- **NFR-07 (Health SLA)**: The system MUST expose `/health` returning HTTP 200 within 1 second of startup.
- **NFR-08 (Architecture Invariants)**: Architectural boundaries must be validated via automated tests in `tests/architecture/`.

---

## 6. End-to-End Claim State Machine (AC-08)

The lifecycle of every cashless claim is governed by the state machine:
```
           +-----------------------+
           |       PRE_AUTH        |
           +-----------------------+
                       | (Pre-Auth Approved)
                       v
           +-----------------------+
           |       ADMITTED        |
           +-----------------------+
                       | (Procedures & Discharge)
                       v
           +-----------------------+
           |      DISCHARGED       |
           +-----------------------+
                       |
            +----------+----------+
            |                     |
            v                     v
    +---------------+     +---------------+
    |    SETTLED    |     |   DISPUTED    |
    +---------------+     +---------------+
            |                     |
            +----------+----------+
                       |
                       v
           +-----------------------+
           |        CLOSED         |
           +-----------------------+
```

### Allowed Transitions:
1. `PRE_AUTH` → `ADMITTED` (Permitted only when pre-authorization status is `APPROVED` or `OVERRIDE_APPROVED`)
2. `ADMITTED` → `DISCHARGED` (Permitted upon submission of discharge summary and final bill)
3. `DISCHARGED` → `SETTLED` (Permitted upon execution of invariant-checked settlement calculation)
4. `DISCHARGED` → `DISPUTED` (Triggered if final bill exceeds pre-auth + buffer cap and cannot be reconciled)
5. `SETTLED` → `CLOSED`
6. `DISPUTED` → `CLOSED`

**Violation Rule**: Any out-of-order transition attempt MUST raise `InvalidClaimStateException`.

---

## 7. Error Handling & Standardized Reason Codes
Standardized error codes returned across all services:
- `POL_NOT_FOUND`: Policy ID does not exist in registry.
- `POL_INACTIVE`: Policy has lapsed, is cancelled, or current date is outside coverage term.
- `HOSP_OUT_OF_NETWORK`: Healthcare facility is not in active network list.
- `SUM_INSURED_EXHAUSTED`: Remaining sum insured is zero.
- `DIAGNOSIS_EXCLUDED`: Clinical condition is explicitly listed in policy exclusions.
- `BILL_EXCEEDS_BUFFER_CAP`: Final bill exceeds `pre_auth_amount + buffer%`.
- `INVALID_CLAIM_STATE`: Out-of-order state machine transition attempted.
- `UNAUTHORIZED_ROLE`: User lacks permission for requested action.
- `PHI_LOGGING_VIOLATION`: Intercepted unredacted health data in log pipeline.

---

## 8. Security & Privacy Rules
1. Authentication tokens must identify `role` and `facility_id` (for hospital actors).
2. Input sanitization applied to all strings.
3. Cryptographic protection: Patient clinical diagnosis is stored securely and never echoed into monitoring streams or log collectors.

---

## 9. Audit Requirements
Every state alteration dispatches an immutable audit event:
```json
{
  "audit_id": "AUD-UUID-7712",
  "case_id": "CASE-9021",
  "timestamp": "2026-10-04T12:00:00Z",
  "actor_id": "USR-HOSP-01",
  "actor_role": "HOSPITAL",
  "action": "SUBMIT_FINAL_BILL",
  "previous_state": "ADMITTED",
  "new_state": "DISCHARGED",
  "metadata": {
    "bill_amount": "45000.00",
    "pre_auth_ref": "PA-4401"
  }
}
```

---

## 10. Global Acceptance Criteria Summary

- **AC-01**: Customer registration and policy linking displaying sum insured, exclusions, and network hospitals.
- **AC-02**: Network hospital eligibility lookup returning `ELIGIBLE` / `NOT_ELIGIBLE` with standardized reason codes.
- **AC-03**: Hospital pre-auth submission entering initial `PENDING` state.
- **AC-04**: Pre-auth lifecycle (`PENDING` → `APPROVED` / `PARTIALLY_APPROVED` / `REJECTED` / `QUERY_RAISED`).
- **AC-05**: Rule-based auto-approval if cost ≤ threshold AND diagnosis is auto-approved.
- **AC-06**: Post-admission procedure and bill submission with buffer enforcement.
- **AC-07**: Settlement calculation: `min(bill, pre_auth + buffer) - deductible - co_pay` with invariant $\ge 0$.
- **AC-08**: Claim state machine enforcing valid transitions and raising `InvalidClaimStateException`.
- **AC-09**: Stubbed notifications and real-time case timeline for customer and hospital.
- **AC-10**: Audited insurer admin override for auto-rejected or queried pre-auths.
