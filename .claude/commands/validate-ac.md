# Custom Command: /validate-ac

## Description
Validates compliance for a specific Acceptance Criteria identifier by executing its designated automated test suite.

## Arguments
- `ac_id`: The Acceptance Criteria ID (e.g. `AC-01`, `AC-02`, ..., `AC-10`)

## Execution Flow
1. Identify matching test file `tests/unit/test_{ac_id.lower()}*.py`.
2. Run pytest targeting that test file with verbose output:
   ```bash
   pytest tests/unit/test_{ac_id.lower()}*.py -v
   ```
3. Report assertion details, execution time, and pass/fail state.
