---
name: eligibility-resolver
description: Skill for evaluating policyholder cashless eligibility and coverage limits
---

# Skill: eligibility-resolver

## Purpose
Validates whether a member has an active health policy and whether cashless intake is permissible at the querying network hospital.

## Inputs
- `member_id` (string): Unique member identifier
- `policy_id` (string): Active policy identifier
- `hospital_id` (string): Querying hospital facility ID
- `lookup_date` (ISO-8601 date string): Date of intake

## Execution Logic & Rules
1. Verify policy exists and status is `ACTIVE`.
2. Verify policy effective dates (`start_date <= lookup_date <= end_date`).
3. Verify `hospital_id` is an active network hospital using `network-hospital-validator`.
4. Check available sum insured (`balance > 0`).
5. If all checks pass:
   - Status: `ELIGIBLE`
   - Return remaining sum insured (Decimal) and exclusions list.
6. If any check fails:
   - Status: `NOT_ELIGIBLE`
   - Return standardized reason codes (`POL_INACTIVE`, `HOSP_OUT_OF_NETWORK`, `SUM_INSURED_EXHAUSTED`).

## Outputs
- `status`: `ELIGIBLE` | `NOT_ELIGIBLE`
- `reason_codes`: list of strings
- `available_balance`: Decimal
- `exclusions`: list of strings

## Validation Rules
- Never return `ELIGIBLE` if hospital is not in network.
- Never use floating-point types for balance amounts.
