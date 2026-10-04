# Custom Command: /settlement-check

## Description
Executes targeted invariant checks on the cashless settlement calculation engine.

## Execution Flow
1. Verify that `src/domain/settlement_rule.py` contains zero floating-point references (`float`).
2. Run edge-case boundary tests in `tests/unit/test_ac07_settlement.py`.
3. Assert that invariant `settlement_amount >= 0` holds across all zero-bill, high-deductible, and buffer-overflow scenarios.
4. Execute `.claude/hooks/settlement-cap-check`.
