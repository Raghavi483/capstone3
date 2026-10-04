---
name: archtest-author
description: Authors and verifies architectural structure tests and layer isolation
---

# Skill: archtest-author

## Purpose
Generates automated structural tests under `tests/architecture/` that enforce clean layered architecture, domain purity, and immutable ledger rules.

## Inputs
- `layer_spec`: Mapping of allowable imports across layers
- `source_root`: Root path of implementation source code (`src/`)

## Execution Logic & Rules
1. Scan AST imports in `src/domain/` to verify zero imports from `controllers`, `services`, `repositories`, `fastapi`, `sqlalchemy`.
2. Scan `src/controllers/` to verify zero direct calls to `repositories`.
3. Scan settlement calculations to verify centralization in `src/domain/settlement_rule.py`.
4. Run pytest against `tests/architecture/`.

## Outputs
- `violations`: list of detected layer boundary violations
- `test_status`: `PASSED` | `FAILED`
