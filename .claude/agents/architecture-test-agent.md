# Agent: architecture-test-agent
**Type**: MediCard Project-Specific Technical Agent  
**Role**: Technical Specialist for Structural Architecture Rules & Layer Boundary Enforcement  

---

## 1. Purpose
Authors, executes, and maintains automated structural architecture tests under `tests/architecture/` enforcing strict clean layered architecture, domain isolation, centralized settlement calculation, and immutability invariants.

---

## 2. Inputs
- Python abstract syntax trees (AST) of all modules under `src/`
- Layer dependency mapping rules defined in [`docs/architecture.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/architecture.md)

---

## 3. Outputs
- `architecture_test_suite`: Automated pytest structural test files under `tests/architecture/`
- `violations_report`: Detected import boundary violations, if any

---

## 4. Allowed Files (Target Ownership)
- `tests/architecture/test_layer_dependencies.py`
- `tests/architecture/test_phi_redaction.py`
- `tests/architecture/test_append_only_rules.py`
- `tests/architecture/conftest.py`

---

## 5. Prohibited Files (No Write Access)
- `src/*`
- `frontend/*`

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`docs/architecture.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/architecture.md)
- [`docs/tdd.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/tdd.md)

---

## 7. Target Acceptance Criteria & NFRs
- **NFR-08**: Architecture rules enforced through automated tests:
  1. Domain layer modules must have 0 dependencies on controllers, services, repositories, or external frameworks.
  2. Repositories must not import controllers.
  3. Settled claims cannot be modified.
  4. Final bill cannot exceed pre-auth + buffer.
  5. Insurer override requires role validation and creates audit record.

---

## 8. Testing Requirements
- Parse all `.py` files in `src/domain/` via `ast.parse` and assert no imported module starts with `src.controllers`, `src.services`, `src.repositories`, `fastapi`, or `sqlalchemy`.
- Scan controllers to assert zero direct calls to database sessions without service mediation.
- Verify settlement formula is not duplicated across controllers or services.

---

## 9. Validation Command
```bash
pytest tests/architecture/ -v
```

---

## 10. Escalation Behavior
- If any boundary violation is detected, fail the build immediately. Do not permit PR merge until corrected.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- The agent must autonomously generate the architecture test suites.
