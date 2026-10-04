---
name: settlement-calculator
description: Calculates cashless settlement payouts with buffer capping and non-negative invariant checks
---

# Skill: settlement-calculator

## Purpose
Executes the centralized financial settlement formula for hospital cashless claim discharge, enforcing policy buffer limits, deductible/co-pay subtractions, and the non-negative payout invariant.

## Inputs
- `final_bill` (Decimal): Total bill submitted by hospital
- `pre_auth_amount` (Decimal): Previously approved pre-auth sum
- `buffer_percentage` (Decimal): Allowed buffer (e.g. Decimal("0.10"))
- `deductible` (Decimal): Customer annual/per-claim deductible
- `co_pay` (Decimal): Customer co-payment amount

## Execution Logic & Rules
1. Calculate allowed cap:
   `bill_cap = pre_auth_amount * (Decimal("1.00") + buffer_percentage)`
2. Determine effective bill eligible for claim:
   `effective_bill = min(final_bill, bill_cap)`
3. Total customer deductions:
   `total_deductions = deductible + co_pay`
4. Calculate raw settlement:
   `raw_settlement = effective_bill - total_deductions`
5. Apply non-negative floor (Invariant AC-07):
   `settlement_amount = max(Decimal("0.00"), raw_settlement)`
6. Patient responsibility:
   `patient_share = (final_bill - effective_bill) + total_deductions`

## Outputs
- `settlement_amount`: Decimal (Insurer payout)
- `effective_bill`: Decimal
- `capped_amount`: Decimal
- `patient_responsibility`: Decimal

## Validation Rules
- All monetary values must be `Decimal`.
- Invariant check: `settlement_amount >= Decimal("0.00")`.
- If `final_bill > pre_auth_amount * (1 + buffer_percentage)`, bill must either be capped or flagged.
