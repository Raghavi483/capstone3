# CLAUDE.md — Domain Layer Directives (`src/domain/`)

## 1. Domain Isolation & Zero-Dependency Rule
- The domain layer is the pure heart of the MediCard business model.
- **ABSOLUTE PROHIBITION**: Modules in `src/domain/` MUST NEVER import from:
  - `src/controllers/`
  - `src/services/`
  - `src/repositories/`
  - Third-party web frameworks (FastAPI, Starlette, Flask)
  - Database drivers or ORMs (SQLAlchemy, sqlite3)
- Modules must contain pure Python dataclasses, business rules, mathematical invariants, and custom exceptions.

## 2. Mandatory Domain Rules & Invariants
- **NFR-01 (Fixed-Point Arithmetic)**: All monetary fields MUST be `decimal.Decimal`. Prohibit `float` casting.
- **AC-07 (Settlement Invariant)**: Invariant `settlement_amount >= 0` must be enforced at initialization of settlement results.
- **AC-06 (Buffer Enforcement)**: Invariant `final_bill <= pre_auth_amount * (1 + buffer_percentage)`.
- **AC-08 (State Transitions)**: Out-of-order transitions must raise `InvalidClaimStateException`.
- **AC-05 (Auto-Approval Rule)**: Pure rule function evaluating cost threshold and diagnosis whitelist.

## 3. Key Domain Files Required
- `eligibility_rule.py`
- `pre_auth_rule.py`
- `settlement_rule.py`
- `claim_state_rule.py`
- `role_boundary_rule.py`
- `network_hospital_rule.py`
