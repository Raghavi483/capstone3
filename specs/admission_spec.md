# Feature Specification: Admission Tracking, Procedure Updates & Claim State Machine
**Feature**: Admission, Bill Submission & Claim Lifecycle  
**Target Acceptance Criteria**: AC-06, AC-08, AC-09  
**Specification File**: `specs/admission_spec.md`  
**Version**: 1.0.0  

---

## 1. Purpose
Defines the tracking of hospital patient admissions, recording of medical procedures, final bill submission with buffer percentage enforcement, the end-to-end claim state machine, and stubbed notification generation.

---

## 2. Actors
- **Hospital**: Confirms patient admission, submits medical procedure codes/descriptions, and submits final itemized discharge bills.
- **Customer**: Receives lifecycle notifications and tracks real-time claim timeline.
- **System**: Enforces state machine transitions and generates stubbed notifications.

---

## 3. Inputs
- Admission Record:
  - `case_id`: UUID
  - `admission_date`: ISO-8601 Date
  - `bed_category`: string (e.g. `GENERAL_WARD`, `ICU`)
- Procedure & Final Bill Submission (AC-06):
  - `case_id`: UUID
  - `procedures`: list of `{procedure_code: str, description: str, cost: Decimal}`
  - `final_bill`: Decimal
  - `discharge_date`: ISO-8601 Date

---

## 4. Outputs
- Admission Confirmation: Updated claim state `ADMITTED`.
- Bill Submission Response:
  - `status`: `ACCEPTED` | `REJECTED_BUFFER_EXCEEDED`
  - `final_bill`: Decimal
  - `pre_auth_amount`: Decimal
  - `allowed_buffer_cap`: Decimal
  - `claim_status`: `DISCHARGED`

---

## 5. Domain Rules
1. **Rule ADM-01 (Admission Prerequisite)**: A case cannot transition to `ADMITTED` unless its pre-authorization is in `APPROVED` or `OVERRIDE_APPROVED` status.
2. **Rule ADM-02 (Final Bill Buffer Cap - AC-06)**:
   - The hospital final bill CANNOT exceed:
     $$\text{bill\_cap} = \text{pre\_auth\_amount} \times (1 + \text{buffer\_percentage})$$
   - Default `buffer_percentage` is configured in policy rules (e.g. `0.10` for 10%).
   - If `final_bill > bill_cap`, the submission MUST be rejected or flagged with error `BILL_EXCEEDS_BUFFER_CAP`.
3. **Rule ADM-03 (State Machine Progression - AC-08)**:
   - State machine strictly enforces:
     `PRE_AUTH` → `ADMITTED` → `DISCHARGED` → `SETTLED` (or `DISPUTED` → `CLOSED`).
   - Invalid or backward transitions raise `InvalidClaimStateException`.
4. **Rule ADM-04 (Notification Stub - AC-09)**:
   - Every state transition triggers a stubbed notification event containing `recipient`, `event_type`, `timestamp`, and `message`.
   - The case status timeline aggregates all transition events chronologically.

---

## 6. State Machine Matrix & Valid Transitions

| From State | To State | Trigger Condition |
| :--- | :--- | :--- |
| `PRE_AUTH` | `ADMITTED` | Pre-auth approved; patient checked in |
| `ADMITTED` | `DISCHARGED` | Treatment completed; final bill submitted <= pre-auth + buffer |
| `DISCHARGED` | `SETTLED` | Settlement calculated and approved |
| `DISCHARGED` | `DISPUTED` | Bill discrepancy or audit hold |
| `SETTLED` | `CLOSED` | Payout acknowledged |
| `DISPUTED` | `CLOSED` | Dispute resolved or rejected |

Any transition not listed above raises `InvalidClaimStateException`.

---

## 7. Error Handling
- `InvalidClaimStateException` (HTTP 409): Raised on invalid transition (e.g. `PRE_AUTH` directly to `SETTLED`).
- `BufferExceededException` (HTTP 422): Raised when final bill exceeds `pre_auth_amount + buffer`.

---

## 8. Security Rules
- Only the admitting hospital can submit admission records and final bills for a given `case_id`.

---

## 9. Audit Requirements
- Every transition emits an audit record with `case_id`, `from_state`, `to_state`, `actor`, `timestamp`.

---

## 10. Acceptance Criteria

### AC-06: Hospital Post-Admission Updates & Final Bill Buffer
- **Scenario 1 (Bill within Buffer Accepted)**:
  - **Given** case `CASE-101` has approved `pre_auth_amount = 50000.00`
  - **And** policy specifies `buffer_percentage = 0.10` (Cap = `55000.00`)
  - **When** hospital submits post-admission procedure details and `final_bill = 53000.00`
  - **Then** the submission is accepted and recorded.

- **Scenario 2 (Bill Exceeding Buffer Rejected)**:
  - **Given** case `CASE-101` has approved `pre_auth_amount = 50000.00` with `10%` buffer (`55000.00`)
  - **When** hospital attempts to submit `final_bill = 62000.00`
  - **Then** the system rejects the bill submission with `BILL_EXCEEDS_BUFFER_CAP`.

### AC-08: Cashless Claim Lifecycle & State Machine
- **Scenario 1 (Valid Lifecycle Progression)**:
  - **Given** a case in `PRE_AUTH` with approved status
  - **When** patient admits → case enters `ADMITTED`
  - **And** patient discharges with final bill → case enters `DISCHARGED`
  - **And** settlement calculation runs → case enters `SETTLED`
  - **And** claim closes → case enters `CLOSED`
  - **Then** all state transitions succeed without error.

- **Scenario 2 (Invalid Transition Exception)**:
  - **Given** a case in `PRE_AUTH` state
  - **When** an actor attempts to transition directly to `SETTLED`
  - **Then** system raises `InvalidClaimStateException`.

### AC-09: Stubbed Notifications & Case Timeline
- **Scenario**: Real-time timeline view across state changes
  - **Given** an active claim case
  - **When** state transitions from `PRE_AUTH` to `ADMITTED` to `DISCHARGED`
  - **Then** stubbed notifications are dispatched for customer and hospital
  - **And** querying `/api/cases/{case_id}/timeline` returns an ordered chronological list of all state events.
