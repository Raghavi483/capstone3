# CLAUDE.md — Root AI-Native Engineering Directives
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform  
**Business Case**: BC-AINE-017  
**Domain**: Insurance — Health Cashless  
**Orchestration Lead**: Antigravity Orchestrator  

---

## 1. CRITICAL NON-NEGOTIABLE DEVELOPMENT RULES

### RULE 1 — NO-HAND-CODING
- **NEVER** write production application code or production tests manually.
- All application implementation code (`src/`), test code (`tests/`), and migrations must be generated strictly by Claude Code agents.
- Orchestrator/Human edits are permitted **ONLY** for: specifications, CLAUDE.md files, AGENTS.md, agent definitions, skills, hooks, commands, plugin configuration, MCP configuration, sprint contracts, documentation, project substrate, and CI configuration.
- **Correction Workflow**: If implementation code needs correction, DO NOT patch it manually.
  1. Identify the defect or failing test.
  2. Determine if specification requires clarification or update.
  3. If needed, update the specification.
  4. Dispatch the task back to the designated Claude Code agent.
  5. Regenerate the implementation.
  6. Run automated validation hooks and tests.
  7. Record the result in the sprint evidence trail.

### RULE 2 — SPECIFICATION IS THE SOURCE OF TRUTH
- Specifications ALWAYS take precedence over implementation: `IF SPECIFICATION != CODE THEN SPECIFICATION WINS`.
- Every important feature must exhibit an unbroken traceability chain:
  $$\text{Requirement} \to \text{Specification} \to \text{Acceptance Criteria (AC-NN)} \to \text{Automated Test} \to \text{Implementation} \to \text{Validation Evidence}$$

### RULE 3 — PR-DRIVEN DEVELOPMENT
- **NEVER** commit directly to the `main` branch. Direct pushes to `main` are strictly forbidden.
- All development must follow the branch lifecycle:
  $$\text{Feature Branch (feat/*)} \to \text{Agent Implementation} \to \text{Tests \& Hooks} \to \text{Evaluator Review} \to \text{PR} \to \text{Merge via git merge --no-ff}$$
- A minimum of 3 PR-driven merges must be preserved across repository history.

### RULE 4 — SYNTHETIC DATA ONLY
- **STRICT PROHIBITION**: Never use real patient, customer, policy, hospital, or Virtusa confidential data.
- All seeds, tests, and mock responses must use clearly synthetic, dummy values.

---

## 2. NON-FUNCTIONAL TECHNICAL CONSTRAINTS

- **NFR-01 (Monetary Fixed-Point Precision)**:
  - All currency calculations (`estimated_cost`, `final_bill`, `pre_auth_amount`, `deductible`, `co_pay`, `settlement_amount`) MUST use `decimal.Decimal`.
  - Floating-point casting (`float`) is strictly prohibited in monetary code paths.
- **NFR-02 & NFR-05 (Append-Only Persistence)**:
  - Tables for decisions, bills, settlements, and administrative overrides are append-only.
  - No physical updates or deletes of historical claim decisions.
- **NFR-03 (PHI Redaction)**:
  - Protected Health Information (diagnosis, procedure description, clinical history) must NEVER appear in plaintext logs.
  - Log entries must reference case IDs, using tokenized or masked data.
- **NFR-04 (Role & Tenant Security Boundaries)**:
  - Roles (`CUSTOMER`, `HOSPITAL`, `INSURER`, `ADMIN`) must be validated at controller boundaries.
  - Hospitals are strictly isolated to viewing and modifying only their own cases.
- **NFR-06 (Structured JSON Logging)**:
  - Logs must output formatted JSON containing `request_id`, `correlation_id`, `case_id`, `actor`, and `event`.
- **NFR-07 (Health SLA)**:
  - Health check endpoint `/health` must return HTTP 200 within 1 second of startup.
- **NFR-08 (Architecture Rules as Tests)**:
  - Layer boundaries (Controllers $\to$ Services $\to$ Domain $\to$ Repositories) must be verified via tests in `tests/architecture/`.
  - Domain rules must have zero dependencies on outer layers.

---

## 3. DOMAIN INVARIANTS & SETTLEMENT FORMULA

- **Settlement Formula (AC-07)**:
  $$\text{bill\_cap} = \text{pre\_auth\_amount} \times (1 + \text{buffer\_percentage})$$
  $$\text{effective\_bill} = \min(\text{final\_bill}, \text{bill\_cap})$$
  $$\text{settlement\_amount} = \max(0, \text{effective\_bill} - \text{deductible} - \text{co\_pay})$$
  $$\text{INVARIANT}: \text{settlement\_amount} \ge 0$$
- **Pre-Auth Auto-Approval (AC-05)**:
  Auto-approved IF `estimated_cost <= threshold` AND `admission_diagnosis in auto_approved_list`.
- **Claim State Machine (AC-08)**:
  `PRE_AUTH` $\to$ `ADMITTED` $\to$ `DISCHARGED` $\to$ `SETTLED` / `DISPUTED` $\to$ `CLOSED`. Invalid transitions raise `InvalidClaimStateException`.

---

## 4. CLAUDE CODE TOKEN OPTIMIZATION DIRECTIVE (Prompt Section 39)

When formulating tasks for Claude Code agents:
1. Always specify the target **AC ID** (e.g. `AC-05`).
2. Point directly to the relevant specification file (e.g. `specs/pre_auth_spec.md`).
3. Explicitly list the exact files to create or modify.
4. Define the exact test command to validate execution.
5. Keep task prompts tightly scoped; avoid open-ended requests.
