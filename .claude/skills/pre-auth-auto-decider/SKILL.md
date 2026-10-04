---
name: pre-auth-auto-decider
description: Evaluates pre-authorization requests for automatic approval against policy rules
---

# Skill: pre-auth-auto-decider

## Purpose
Applies automated decision rules to pre-authorization requests, approving qualifying standard procedures up to policy caps without human latency.

## Inputs
- `estimated_cost` (Decimal): Proposed treatment cost
- `admission_diagnosis` (string): Clinical condition description/code
- `policy_rules` (dict):
  - `auto_approval_threshold` (Decimal)
  - `auto_approved_diagnoses` (list of strings)
  - `category_cap` (Decimal)
  - `remaining_sum_insured` (Decimal)

## Execution Logic & Rules
1. Compare `estimated_cost <= policy_rules.auto_approval_threshold`.
2. Check if `admission_diagnosis.upper()` is in `policy_rules.auto_approved_diagnoses`.
3. Verify `estimated_cost <= policy_rules.remaining_sum_insured`.
4. IF all 3 conditions hold:
   - Decision: `APPROVED`
   - Authorized Amount: `min(estimated_cost, policy_rules.category_cap)`
   - Reason Code: `AUTO_APPROVED_STANDARD_CARE`
5. ELSE:
   - Decision: `PENDING`
   - Authorized Amount: `0.00`
   - Reason Code: `ROUTED_TO_MANUAL_ADJUDICATION`

## Outputs
- `decision`: `APPROVED` | `PENDING`
- `authorized_amount`: Decimal
- `reason_code`: string

## Validation Rules
- Must use `Decimal` for all arithmetic comparisons.
- Must not auto-approve if diagnosis is in policy exclusions.
