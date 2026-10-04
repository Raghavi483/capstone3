# Custom Command: /validate-medi-card

## Description
Executes the comprehensive MediCard validation pipeline across code formatting, linting, unit tests, architecture tests, and guardrail hooks.

## Workflow
1. Run local pre-commit guardrail hooks:
   - `phi-redaction-check`
   - `settlement-cap-check`
   - `role-boundary-check`
   - `architecture-boundary-check`
2. Run pytest suite with coverage:
   ```bash
   pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term-missing tests/
   ```
3. Run structural architecture tests:
   ```bash
   pytest tests/architecture/ -v
   ```
4. Check that 100% of tests pass and no AC regressions exist.
