# Feature Specification: Pre-Authorization Submission & Decisioning Engine
**Feature**: Pre-Authorization Lifecycle & Auto-Approval  
**Target Acceptance Criteria**: AC-03, AC-04, AC-05  
**Specification File**: `specs/pre_auth_spec.md`  
**Version**: 1.0.0  

---

## 1. Purpose
Defines the submission of pre-authorization requests by network hospitals, rule-driven auto-approval evaluation against configured cost thresholds and diagnostic lists, and the core pre-authorization lifecycle.

---

## 2. Actors
- **Hospital**: Submits pre-authorization request with clinical diagnosis, estimated cost, and admission schedule.
- **Pre-Auth Decisioning Engine**: Automated rule evaluator.
- **Insurer Adjudicator**: Reviews non-auto-approved or queried submissions.
- **Customer**: Receives notification of decision and views case timeline.

---

## 3. Inputs
Pre-Auth Submission Payload:
- `member_id`: string (e.g. `MEM-100234`)
- `policy_id`: string (e.g. `POL-550912`)
- `hospital_id`: string (e.g. `HOSP-001`)
- `admission_diagnosis`: string (e.g. `ACUTE_APPENDICITIS`)
- `estimated_cost`: Decimal (e.g. `45000.00`)
- `expected_admission_date`: ISO-8601 Date (e.g. `2026-10-10`)
- `doctor_notes`: string (optional)

---

## 4. Outputs
Pre-Auth Submission / Decision Response:
- `pre_auth_id`: string (UUID)
- `case_id`: string (UUID)
- `status`: `PENDING` | `APPROVED` | `PARTIALLY_APPROVED` | `REJECTED` | `QUERY_RAISED`
- `authorized_amount`: Decimal
- `decision_reason_code`: string (e.g. `AUTO_APPROVED_STANDARD_CARE`, `MANUAL_REVIEW_REQUIRED`)
- `policy_version`: string
- `created_at`: ISO-8601 timestamp

---

## 5. Domain Rules
1. **Rule PRE-01 (Mandatory Intake Fields)**: Submission must validate presence and format of member, policy, hospital, diagnosis, positive estimated cost, and future or present admission date. Initial status enters `PENDING`.
2. **Rule PRE-02 (Auto-Approval Gate - AC-05)**:
   - A pre-authorization is **automatically approved** IF:
     1. `estimated_cost <= policy.auto_approval_threshold` (e.g. `50000.00` Decimal), AND
     2. `admission_diagnosis` is present in `policy.auto_approved_diagnoses` (e.g., `['ACUTE_APPENDICITIS', 'CATARACT_SURGERY', 'DENGUE_FEVER_STANDARD']`), AND
     3. Hospital is active in network, AND
     4. `estimated_cost <= remaining_sum_insured`.
   - **Authorized Cap**: Upon auto-approval, `authorized_amount = min(estimated_cost, policy.category_cap)`.
3. **Rule PRE-03 (Manual Queue Escalation)**: If estimated cost exceeds the threshold OR diagnosis is not in the auto-approved whitelist, pre-auth remains in `PENDING` (or transitions to `QUERY_RAISED` if documentation is deficient) for adjudicator evaluation.
4. **Rule PRE-04 (Append-Only Decision Log)**: Every decision (auto or manual) creates a new immutable record in `pre_auth_decisions`.

---

## 6. State Transitions
Pre-Auth Decision Machine:
```
           +-----------------------+
           |       SUBMITTED       |
           +-----------------------+
                       |
                       v
           +-----------------------+
           |        PENDING        |
           +-----------------------+
            /         |           \
           /          |            \
          v           v             v
    +----------+ +----------+ +--------------+
    | APPROVED | | REJECTED | | QUERY_RAISED |
    +----------+ +----------+ +--------------+
                                    |
                                    v (Response Provided)
                              +-----------+
                              | PENDING   |
                              +-----------+
```

---

## 7. Error Handling
- `400 Bad Request`: If `estimated_cost <= 0`, missing diagnosis, or expected admission date in past.
- `404 Not Found`: If member or policy is not found.
- `422 Unprocessable Entity`: If `admission_diagnosis` matches a strict policy exclusion list.

---

## 8. Security Rules
- Hospitals can only submit pre-authorizations where `hospital_id` matches their authenticated facility credentials.
- Diagnosis and medical clinical notes must be redacted from system logs (**NFR-03**).

---

## 9. Audit Requirements
- Dispatch audit record with `case_id`, `pre_auth_id`, `decision`, `authorized_amount`, `decision_rule`, `timestamp`.

---

## 10. Acceptance Criteria

### AC-03: Pre-Authorization Request Submission
- **Scenario**: Hospital submits pre-authorization request
  - **Given** an eligible member `MEM-100234` at network hospital `HOSP-001`
  - **When** the hospital submits a pre-auth request with:
    - `admission_diagnosis`: `"CHOLECYSTITIS"`
    - `estimated_cost`: `60000.00`
    - `expected_admission_date`: `"2026-10-12"`
  - **Then** the request is accepted, a unique `case_id` and `pre_auth_id` are generated
  - **And** the initial status is set to `PENDING`.

### AC-04: Pre-Authorization Lifecycle & Reason Codes
- **Scenario**: Adjudication transition with policy reason codes
  - **Given** a pre-authorization in `PENDING` state
  - **When** an adjudicator reviews and decides `APPROVED`, `PARTIALLY_APPROVED`, `REJECTED`, or `QUERY_RAISED`
  - **Then** the decision is recorded with a mandatory policy reason code (e.g., `DOCS_INSUFFICIENT`, `POLICY_LIMIT_REACHED`)
  - **And** the policy version is persisted alongside the decision record.

### AC-05: Auto-Approval Decisioning
- **Scenario 1 (Auto-Approval Success)**:
  - **Given** policy `POL-550912` has `auto_approval_threshold = 50000.00`
  - **And** `"ACUTE_APPENDICITIS"` is in `auto_approved_diagnoses`
  - **When** hospital submits pre-auth with `estimated_cost = 45000.00` for `"ACUTE_APPENDICITIS"`
  - **Then** the pre-auth engine automatically assigns status `APPROVED`
  - **And** sets `authorized_amount = 45000.00`
  - **And** records reason code `AUTO_APPROVED_STANDARD_CARE`.

- **Scenario 2 (Exceeds Threshold - Routes to Adjudicator)**:
  - **Given** policy `POL-550912` has `auto_approval_threshold = 50000.00`
  - **When** hospital submits pre-auth with `estimated_cost = 75000.00` for `"ACUTE_APPENDICITIS"`
  - **Then** auto-approval does not trigger
  - **And** status remains `PENDING` awaiting adjudicator manual review.
