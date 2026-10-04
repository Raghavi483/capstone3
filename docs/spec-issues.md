# Specification Issues & Resolution Log
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Document**: `docs/spec-issues.md`  
**Purpose**: Document all identified ambiguities, inconsistencies, or edge cases in specifications and record their formal resolution before implementation.

---

## 1. Specification Audit Summary

All 8 specifications were systematically audited against the 10 Functional Acceptance Criteria (AC-01 through AC-10) and 8 Non-Functional Requirements (NFR-01 through NFR-08).

---

## 2. Issues & Formal Resolutions

### Issue SPEC-01: Disambiguation of Buffer Representation in AC-07 Settlement
- **Specification**: `specs/settlement_spec.md` & `specs/admission_spec.md`
- **Ambiguity**: The brief states `settlement_amount = min(final_bill, pre_auth_amount + buffer) - deductible - co_pay`. In real-world contracts, "buffer" is often specified as a percentage (e.g., 10%) rather than an absolute dollar figure. Without clear definitions, implementations may calculate `pre_auth_amount + 0.10` or vary in rounding.
- **Resolution**:
  Explicit definitions and formulas codified in `specs/settlement_spec.md` (v1.1.0):
  1. `buffer_percentage` represents the ratio (e.g. `Decimal("0.10")`).
  2. `buffer_amount = pre_auth_amount * buffer_percentage`.
  3. `bill_cap = pre_auth_amount + buffer_amount`.
  4. `effective_bill = min(final_bill, bill_cap)`.
  5. `settlement_amount = max(0, effective_bill - deductible - co_pay)`.
  6. Any portion of `final_bill` exceeding `bill_cap` is attributed to `patient_responsibility`.
- **Status**: RESOLVED & CODIFIED.

---

### Issue SPEC-02: Claim State Machine Terminal State for Disputes
- **Specification**: `specs/admission_spec.md`
- **Ambiguity**: AC-08 specifies `DISCHARGED -> SETTLED / DISPUTED -> CLOSED`. The transition conditions for moving from `DISPUTED` to `CLOSED` needed explicit triggers.
- **Resolution**:
  A dispute can reach `CLOSED` through either:
  1. Administrative arbitration where an agreed settlement adjustment is appended, moving `DISPUTED` $\to$ `SETTLED` $\to$ `CLOSED`.
  2. Claim rejection/cancellation where dispute is upheld without payout, moving `DISPUTED` $\to$ `CLOSED` directly with reason `DISPUTE_REJECTED`.
- **Status**: RESOLVED & CODIFIED.

---

### Issue SPEC-03: Pre-Authorization Override Authorization vs Policy Caps
- **Specification**: `specs/adjudication_spec.md`
- **Ambiguity**: Can an Insurer Admin override a pre-authorization to an amount higher than the member's remaining annual sum insured?
- **Resolution**:
  No. Rule ADJ-02 explicitly forbids overrides exceeding `policy.remaining_sum_insured`. An override can grant an exception for clinical necessity or bypass the auto-approval threshold, but cannot create phantom coverage exceeding contractual policy limits.
- **Status**: RESOLVED & CODIFIED.

---

### Issue SPEC-04: PHI Redaction Boundary in Error Responses
- **Specification**: `specs/app_spec.md`
- **Ambiguity**: NFR-03 prohibits logging PHI in plaintext. Does this apply to client-facing HTTP 422 error messages?
- **Resolution**:
  Yes. REST error responses must return generic or standardized error codes (e.g., `{"error_code": "DIAGNOSIS_EXCLUDED", "message": "The proposed diagnosis is excluded under policy terms."}`) rather than echoing back detailed clinical descriptions or patient health histories in raw log dumps.
- **Status**: RESOLVED & CODIFIED.
