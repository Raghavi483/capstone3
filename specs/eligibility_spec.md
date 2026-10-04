# Feature Specification: Customer Registration & Eligibility Verification
**Feature**: Eligibility & Policy Coverage Management  
**Target Acceptance Criteria**: AC-01, AC-02  
**Specification File**: `specs/eligibility_spec.md`  
**Version**: 1.0.0  

---

## 1. Purpose
Defines the functional requirements, domain rules, API contracts, and validation criteria for customer registration, policy linking, coverage visibility, and real-time hospital eligibility lookups.

---

## 2. Actors
- **Customer**: Registers account and views policy benefits (sum insured, remaining balance, exclusions, network hospitals).
- **Network Hospital**: Queries member eligibility at intake desk using member ID and policy ID.
- **Admin**: Maintains policy master and network hospital linkages.

---

## 3. Inputs
- Customer Registration: `full_name`, `email`, `phone_number`, `member_id`, `policy_id`.
- Eligibility Query: `member_id` (string), `policy_id` (string), `hospital_id` (string).

---

## 4. Outputs
- Registration Response: Profile details, linked policy status, sum insured, exclusions list, list of network hospitals.
- Eligibility Query Response:
  - `status`: `ELIGIBLE` or `NOT_ELIGIBLE`
  - `member_name`: string
  - `policy_status`: `ACTIVE` | `EXPIRED` | `LAPSED`
  - `available_sum_insured`: Decimal
  - `reason_codes`: list of standardized reason codes (e.g. `['HOSP_OUT_OF_NETWORK']`)
  - `timestamp`: ISO-8601 string

---

## 5. Domain Rules
1. **Rule ELIG-01 (Active Policy)**: A member is eligible if and only if their policy exists, status is `ACTIVE`, and effective dates enclose the lookup date.
2. **Rule ELIG-02 (Network Hospital Membership)**: The querying hospital MUST be registered as an active in-network provider. If not in network, status MUST be `NOT_ELIGIBLE` with reason `HOSP_OUT_OF_NETWORK`.
3. **Rule ELIG-03 (Sufficient Balance)**: If remaining sum insured is `<= 0`, status MUST be `NOT_ELIGIBLE` with reason `SUM_INSURED_EXHAUSTED`.
4. **Rule ELIG-04 (Decimal Integrity)**: Sum insured and balance values must use `Decimal`.

---

## 6. State Transitions
- Customer Policy: `PENDING_LINK` → `LINKED_ACTIVE` → `SUSPENDED` / `EXPIRED`.
- Eligibility Check is an idempotent, read-only domain operation with audit logging.

---

## 7. Error Handling
- `404 Not Found`: If `member_id` or `policy_id` does not exist (`POL_NOT_FOUND`).
- `400 Bad Request`: If lookup payload contains invalid formatting.
- `403 Forbidden`: If unauthenticated actor attempts query.

---

## 8. Security Rules
- Customer can only query their own policy details.
- Hospital cannot look up customers without supplying both `member_id` and `policy_id`.
- Hospital lookup logs must record `hospital_id` and `timestamp`.

---

## 9. Audit Requirements
- Every eligibility check (whether eligible or ineligible) writes an entry to `audit_logs` capturing `hospital_id`, `member_id`, `status`, and `reason_codes`.

---

## 10. Acceptance Criteria

### AC-01: Customer Registration & Coverage Visibility
- **Scenario**: Customer registers and links an active health policy
  - **Given** a valid customer with unlinked policy ID `POL-550912`
  - **When** the customer registers and links their policy
  - **Then** the account is successfully created and returns:
    - `sum_insured`: `500000.00` (Decimal)
    - `exclusions`: list of excluded conditions (e.g., `["COSMETIC_SURGERY", "EXPERIMENTAL_THERAPY"]`)
    - `network_hospitals`: list of affiliated hospital IDs and names
  - **And** the customer can retrieve this coverage information on their dashboard.

### AC-02: Network Hospital Eligibility Lookup
- **Scenario 1 (Successful Eligibility)**:
  - **Given** an active policy `POL-550912` with positive remaining balance `500000.00`
  - **And** hospital `HOSP-001` is an active network hospital
  - **When** the hospital looks up member `MEM-100234` and policy `POL-550912`
  - **Then** the system returns `status: "ELIGIBLE"` with `reason_codes: []` and available balance.

- **Scenario 2 (Hospital Out of Network)**:
  - **Given** hospital `HOSP-999` is NOT an active network provider
  - **When** the hospital looks up member `MEM-100234` and policy `POL-550912`
  - **Then** the system returns `status: "NOT_ELIGIBLE"` with reason code `HOSP_OUT_OF_NETWORK`.

- **Scenario 3 (Exhausted Sum Insured)**:
  - **Given** member `MEM-100234` has an active policy with remaining sum insured `0.00`
  - **When** hospital `HOSP-001` queries eligibility
  - **Then** the system returns `status: "NOT_ELIGIBLE"` with reason code `SUM_INSURED_EXHAUSTED`.
