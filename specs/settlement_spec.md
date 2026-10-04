# Feature Specification: Settlement Calculation & Payout Ledger
**Feature**: Settlement Engine & Financial Invariant Enforcement  
**Target Acceptance Criteria**: AC-07, NFR-01, NFR-02  
**Specification File**: `specs/settlement_spec.md`  
**Version**: 1.1.0  
**Audit Status**: VERIFIED (Audited for term disambiguation)  

---

## 1. Purpose
Specifies the mathematical calculation of insurer cashless settlement payouts to network hospitals, enforcement of the zero-floor non-negative invariant, fixed-point decimal arithmetic, and append-only settlement persistence.

---

## 2. Actors
- **Hospital**: Submits settlement request upon patient discharge.
- **Settlement Engine**: Executes the centralized calculation formula.
- **Insurer Finance**: Reviews and disburses stubbed settlement payments.
- **Customer**: Inspects breakdown of out-of-pocket costs (deductibles, co-pay) and insurer payment.

---

## 3. Disambiguated Terminology & Variable Definitions
To eliminate ambiguity, all monetary terms are strictly distinguished and defined as follows:

| Term Variable | Type | Definition & Mathematical Formula |
| :--- | :--- | :--- |
| `pre_auth_amount` | `Decimal` | Authorized coverage cap approved during pre-authorization. |
| `buffer_percentage` | `Decimal` | Configured policy variance ratio (e.g. `Decimal("0.10")` represents 10%). |
| `buffer_amount` | `Decimal` | Explicit monetary buffer: $$\text{buffer\_amount} = \text{pre\_auth\_amount} \times \text{buffer\_percentage}$$ |
| `bill_cap` | `Decimal` | Maximum bill amount eligible for cashless settlement: $$\text{bill\_cap} = \text{pre\_auth\_amount} + \text{buffer\_amount}$$ |
| `final_bill` | `Decimal` | Total itemized invoice submitted by hospital upon patient discharge. |
| `effective_bill` | `Decimal` | Bill amount considered for insurance settlement: $$\text{effective\_bill} = \min(\text{final\_bill}, \text{bill\_cap})$$ |
| `deductible` | `Decimal` | Policyholder deductible subtracted before insurer payout. |
| `co_pay` | `Decimal` | Policyholder co-payment obligation subtracted before insurer payout. |
| `settlement_amount` | `Decimal` | Net insurer payout to network hospital: $$\text{settlement\_amount} = \max(0, \text{effective\_bill} - \text{deductible} - \text{co\_pay})$$ |
| `patient_responsibility` | `Decimal` | Total out-of-pocket amount payable by patient to hospital: $$\text{patient\_responsibility} = (\text{final\_bill} - \text{effective\_bill}) + \text{deductible} + \text{co\_pay}$$ |

---

## 4. Inputs
Settlement Calculation Input DTO:
- `case_id`: UUID
- `final_bill`: Decimal (e.g. `52000.00`)
- `pre_auth_amount`: Decimal (e.g. `50000.00`)
- `buffer_percentage`: Decimal (e.g. `0.10`)
- `deductible`: Decimal (e.g. `2000.00`)
- `co_pay`: Decimal (e.g. `5000.00`)

---

## 5. Outputs
Settlement Calculation Result DTO:
- `settlement_id`: UUID
- `case_id`: UUID
- `buffer_amount`: Decimal
- `bill_cap`: Decimal
- `effective_bill`: Decimal
- `deductions_total`: Decimal (`deductible + co_pay`)
- `settlement_amount`: Decimal (Insurer payout to hospital)
- `patient_responsibility`: Decimal
- `settlement_status`: `SETTLED`
- `calculated_at`: ISO-8601 timestamp

---

## 6. Domain Rules & Invariants
1. **Rule SET-01 (Canonical Formula & Non-Negative Invariant - AC-07)**:
   - Calculation sequence:
     $$\text{buffer\_amount} = \text{pre\_auth\_amount} \times \text{buffer\_percentage}$$
     $$\text{bill\_cap} = \text{pre\_auth\_amount} + \text{buffer\_amount}$$
     $$\text{effective\_bill} = \min(\text{final\_bill}, \text{bill\_cap})$$
     $$\text{settlement\_amount} = \max(0, \text{effective\_bill} - \text{deductible} - \text{co\_pay})$$
   - **MANDATORY MATHEMATICAL INVARIANT**:
     $$\text{settlement\_amount} \ge 0$$
2. **Rule SET-02 (Fixed-Point Arithmetic - NFR-01)**:
   - All variables and intermediate operations MUST use `decimal.Decimal`.
   - Floating-point representations (`float`) are strictly forbidden. Any `float` passed raises `TypeError`.
3. **Rule SET-03 (Single Source of Truth)**:
   - Settlement calculation logic MUST be centralized inside `src/domain/settlement_rule.py`.
   - Duplication across controllers or services is prohibited and enforced via hook `settlement-cap-check`.
4. **Rule SET-04 (Append-Only Persistence - NFR-02)**:
   - Once saved in `claim_settlements`, the record is immutable. No updates or deletions are allowed.

---

## 7. State Transitions
Claim state transitions from `DISCHARGED` $\to$ `SETTLED`.

---

## 8. Error Handling
- `TypeError`: If any input is passed as a `float` instead of `Decimal`.
- `ValueError`: If any monetary value is negative.
- `InvalidClaimStateException`: If settlement is requested before `DISCHARGED` state.

---

## 9. Security Rules
- Only authorized Insurer Finance or internal settlement daemon can finalize settlement payouts.

---

## 10. Audit Requirements
- Settlement generation dispatches an immutable audit record capturing all terms: `case_id`, `settlement_id`, `final_bill`, `bill_cap`, `effective_bill`, `deductible`, `co_pay`, `settlement_amount`, `timestamp`.

---

## 11. Acceptance Criteria

### AC-07: Settlement Calculation & Invariant Enforcement
- **Scenario 1 (Standard Settlement with Buffer Cap)**:
  - **Given** `pre_auth_amount = 50000.00`, `buffer_percentage = 0.10`
  - **And** `buffer_amount = 5000.00`, resulting in `bill_cap = 55000.00`
  - **And** `final_bill = 52000.00`, `deductible = 2000.00`, `co_pay = 5000.00`
  - **When** the settlement is calculated
  - **Then** `effective_bill = 52000.00`
  - **And** `settlement_amount = 45000.00` ($52000 - 2000 - 5000$)
  - **And** `patient_responsibility = 7000.00` ($2000 + 5000$)
  - **And** invariant `settlement_amount >= 0` is satisfied.

- **Scenario 2 (High Deductible Non-Negative Floor)**:
  - **Given** `final_bill = 10000.00`, `pre_auth_amount = 10000.00`, `buffer_percentage = 0.00`
  - **And** `deductible = 8000.00` and `co_pay = 5000.00` (Total deductions = 13000.00)
  - **When** the settlement is calculated
  - **Then** raw difference is $-3000.00$
  - **And** `settlement_amount` is floored at `0.00`
  - **And** invariant `settlement_amount >= 0` is strictly maintained.

- **Scenario 3 (Final Bill Exceeds Bill Cap)**:
  - **Given** `pre_auth_amount = 100000.00`, `buffer_percentage = 0.10` (`bill_cap = 110000.00`)
  - **And** `final_bill = 120000.00` (Exceeds bill cap by 10000.00)
  - **And** `deductible = 0.00`, `co_pay = 10000.00`
  - **When** the settlement is calculated
  - **Then** `effective_bill = 110000.00` (Capped)
  - **And** `settlement_amount = 100000.00` ($110000 - 10000$)
  - **And** `patient_responsibility = 20000.00` ($10000 \text{ excess} + 10000 \text{ co-pay}$).
