# Feature Specification: Adjudication Workbench & Administrator Override
**Feature**: Claims Adjudication & Insurer Governance  
**Target Acceptance Criteria**: AC-04, AC-10  
**Specification File**: `specs/adjudication_spec.md`  
**Version**: 1.0.0  

---

## 1. Purpose
Specifies the adjudicator workbench for manual pre-auth evaluation, query resolution workflows, and the insurer administrator override governance mechanism for auto-rejected or escalated claims.

---

## 2. Actors
- **Insurer Adjudicator**: Evaluates pending pre-authorizations, inspects clinical estimates, issues partial or full approvals, or raises queries.
- **Insurer Admin**: Holds elevated governance authority to override auto-rejected decisions or escalated queries with mandatory justification.
- **Hospital**: Responds to raised queries with supplementary details.

---

## 3. Inputs
- Adjudicator Decision:
  - `case_id`: UUID
  - `pre_auth_id`: UUID
  - `decision`: `APPROVED` | `PARTIALLY_APPROVED` | `REJECTED` | `QUERY_RAISED`
  - `authorized_amount`: Decimal
  - `reason_code`: string (e.g. `CLINICAL_JUSTIFICATION_MET`, `POLICY_SUB_LIMIT_APPLIED`)
  - `adjudicator_notes`: string
- Administrator Override (AC-10):
  - `case_id`: UUID
  - `pre_auth_id`: UUID
  - `override_decision`: `APPROVED` | `PARTIALLY_APPROVED`
  - `override_amount`: Decimal
  - `reason`: string (Mandatory non-empty justification)
  - `actor_id`: string (Authenticated admin identity)
  - `timestamp`: ISO-8601 string

---

## 4. Outputs
- Adjudication Confirmation: Updated case status, decision record, timestamped audit reference.
- Override Response: Overridden pre-auth state, updated authorized amount, immutable audit log entry.

---

## 5. Domain Rules
1. **Rule ADJ-01 (Adjudicator Authority)**: Only actors with role `INSURER` or `ADMIN` can execute manual decisions.
2. **Rule ADJ-02 (Override Pre-requisites - AC-10)**:
   - An administrator override is permitted ONLY if:
     1. The current pre-auth state is `REJECTED` (auto or manual) OR `QUERY_RAISED` (escalated).
     2. The actor holds role `ADMIN`.
     3. A non-empty, detailed `reason` is supplied (minimum 10 characters).
     4. `override_amount <= policy.sum_insured_balance`.
3. **Rule ADJ-03 (Immutability & Non-Destructive Update)**: The original rejection or query record is preserved untouched in history. The override is appended as an `OVERRIDE_DECISION` record with actor ID and timestamp.

---

## 6. State Transitions
```
    +-------------------+           +-----------------------+
    | AUTO_REJECTED /   |  Admin    |   OVERRIDE_APPROVED   |
    | QUERY_RAISED      | --------> | (Authorized Amount set|
    +-------------------+  Override |  and Audited)         |
                                    +-----------------------+
```

---

## 7. Error Handling
- `403 Forbidden`: Non-admin actor attempting override.
- `400 Bad Request`: Empty override reason or override amount exceeding policy limit.
- `409 Conflict`: Attempting to override a pre-auth that is already `APPROVED` or `CLOSED`.

---

## 8. Security Rules
- Elevated endpoint `/api/admin/override` protected by role validator `role_boundary_rule.py`.
- Any unauthorized access attempt logged with severity `CRITICAL`.

---

## 9. Audit Requirements
- All override operations MUST be committed to `audit_logs` with `actor_id`, `actor_role`, `case_id`, `justification`, `override_amount`, and `timestamp`.

---

## 10. Acceptance Criteria

### AC-10: Insurer Admin Override
- **Scenario 1 (Successful Admin Override of Auto-Rejected Pre-Auth)**:
  - **Given** pre-authorization `PA-8821` has status `REJECTED` due to reason `AUTO_REJECT_LIMIT_EXCEEDED`
  - **And** the actor is authenticated as `admin_user_01` with role `ADMIN`
  - **When** the admin submits an override request with:
    - `override_decision`: `"APPROVED"`
    - `override_amount`: `50000.00`
    - `reason`: `"Exceptional clinical necessity approved by medical director"`
  - **Then** the pre-auth status transitions to `APPROVED`
  - **And** an immutable audit record is created capturing `actor = "admin_user_01"`, timestamp, and the exact justification.

- **Scenario 2 (Non-Admin Role Rejection)**:
  - **Given** pre-authorization `PA-8821` has status `REJECTED`
  - **And** the actor is authenticated with role `HOSPITAL` or `CUSTOMER`
  - **When** the actor attempts to invoke the override endpoint
  - **Then** the request is blocked with HTTP 403 Forbidden
  - **And** no state changes or overrides are executed.

- **Scenario 3 (Missing Justification Reason Rejection)**:
  - **Given** an admin user
  - **When** the admin attempts an override with empty reason `""`
  - **Then** the system rejects the operation with HTTP 400 Bad Request.
