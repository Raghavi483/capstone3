# Feature Specification: Settlement Calculation & Payout Ledger
**Feature**: Settlement Engine & Financial Invariant Enforcement  
**Target Acceptance Criteria**: AC-07, NFR-01, NFR-02  
**Specification File**: `specs/settlement_spec.md`  
**Version**: 1.0.0  

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

## 3. Inputs
Settlement Calculation Input:
- `case_id`: UUID
- `final_bill`: Decimal (e.g. `52000.00`)
- `pre_auth_amount`: Decimal (e.g. `50000.00`)
- `buffer_percentage`: Decimal (e.g. `0.10`)
- `deductible`: Decimal (e.g. `2000.00`)
- `co_pay`: Decimal (e.g. `5000.00`)

---

## 4. Outputs
Settlement Calculation Result:
- `settlement_id`: UUID
- `case_id`: UUID
- `effective_bill`: Decimal
- `deductions_total`: Decimal
- `settlement_amount`: Decimal (Insurer payout to hospital)
- `patient_responsibility`: Decimal (deductible + co_pay + any over-cap variance)
- `settlement_status`: `SETTLED`
- `calculated_at`: ISO-8601 timestamp

---

## 5. Domain Rules
1. **Rule SET-01 (Formula Invariant - AC-07)**:
   - The insurer settlement amount is calculated strictly via:
     $$\text{bill\_cap} = \text{pre\_auth\_amount} \times (1 + \text{buffer\_percentage})$$
     $$\text{effective\_bill} = \min(\text{final\_bill}, \text{bill\_cap})$$
     $$\text{raw\_settlement} = \text{effective\_bill} - \text{deductible} - \text{co\_pay}$$
     $$\text{settlement\_amount} = \max(0, \text{raw\_settlement})$$
   - **MANDATORY INVARIANT**: $\text{settlement\_amount} \ge 0$.
2. **Rule SET-02 (Fixed-Point Arithmetic - NFR-01)**:
   - All monetary variables and intermediate terms MUST be computed using `decimal.Decimal`.
   - Floating-point representations (`float`) are strictly forbidden.
3. **Rule SET-03 (Single Source of Truth)**:
   - Settlement calculation logic MUST be centralized inside `src/domain/settlement_rule.py`.
   - Duplication of the formula across controllers, services, or repository queries is an architectural violation.
4. **Rule SET-04 (Append-Only Persistence - NFR-02)**:
   - Once computed and saved in `claim_settlements`, the record is immutable. No modifications or deletions are allowed. Any correction requires an append-only adjustment entry.

---

## 6. State Transitions
Claim state transitions from `DISCHARGED` → `SETTLED`.

---

## 7. Error Handling
- `TypeError`: If any input is passed as a `float` instead of `Decimal`.
- `ValueError`: If any input monetary value is negative.
- `InvalidClaimStateException`: If settlement is requested before `DISCHARGED` state.

---

## 8. Security Rules
- Only authorized Insurer Finance or system settlement daemon can finalize settlement payouts.

---

## 9. Audit Requirements
- Settlement generation dispatches an audit record capturing: `case_id`, `settlement_id`, `final_bill`, `effective_bill`, `deductible`, `co_pay`, `settlement_amount`, `timestamp`.

---

## 10. Acceptance Criteria

### AC-07: Settlement Calculation & Invariant Enforcement
- **Scenario 1 (Standard Settlement)**:
  - **Given** `final_bill = 50000.00`, `pre_auth_amount = 50000.00`, `buffer_percentage = 0.10`
  - **And** `deductible = 2000.00` and `co_pay = 5000.00`
  - **When** the settlement is calculated
  - **Then** `effective_bill = 50000.00`
  - **And** `settlement_amount = 43000.00` (min(50000, 55000) - 2000 - 5000)
  - **And** invariant `settlement_amount >= 0` is satisfied.

- **Scenario 2 (High Deductible Non-Negative Floor)**:
  - **Given** `final_bill = 10000.00`, `pre_auth_amount = 10000.00`, `buffer_percentage = 0.00`
  - **And** `deductible = 8000.00` and `co_pay = 5000.00` (Total deductions = 13000.00)
  - **When** the settlement is calculated
  - **Then** `raw_settlement` would be `-3000.00`
  - **And** `settlement_amount` is capped at `0.00`
  - **And** invariant `settlement_amount >= 0` is strictly maintained.

- **Scenario 3 (Final Bill Exceeds Pre-Auth but Within Buffer)**:
  - **Given** `pre_auth_amount = 100000.00`, `buffer_percentage = 0.10` (Cap = `110000.00`)
  - **And** `final_bill = 108000.00`, `deductible = 0.00`, `co_pay = 10000.00`
  - **When** the settlement is calculated
  - **Then** `effective_bill = 108000.00`
  - **And** `settlement_amount = 98000.00`.
