# Capstone Compliance & Gap Matrix
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform  
**Business Case ID**: BC-AINE-017  
**Audit Date**: 2026-10-04  
**Auditor**: Lead AI-Native Engineering Orchestrator  
**Status Taxonomy**: `COMPLETE` | `PARTIAL` | `SCAFFOLDED` | `PLACEHOLDER` | `MISSING` | `BLOCKED` | `VERIFIED`  

---

## 1. Compliance Matrix

| Requirement | Source | Current Status | Evidence | Gap | Next Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AC-01: Customer Registration & Policy Coverage** | Brief Sec 5.1 | SCAFFOLDED | `specs/eligibility_spec.md`, `specs/network_admin_spec.md` | No application code or tests exist. | Generate domain validator, services, and `test_ac01_*.py` via `eligibility-agent` in Sprint 2. |
| **AC-02: Hospital Eligibility Lookup** | Brief Sec 5.1 | SCAFFOLDED | `specs/eligibility_spec.md`, `.claude/skills/eligibility-resolver/SKILL.md` | No lookup API endpoint or unit tests exist. | Generate `src/domain/eligibility_rule.py` and `test_ac02_*.py` in Sprint 2. |
| **AC-03: Pre-Auth Submission (Initial PENDING)** | Brief Sec 5.1 | SCAFFOLDED | `specs/pre_auth_spec.md`, `.claude/agents/pre-auth-decider-agent.md` | No pre-auth intake service, schema, or test exists. | Generate pre-auth intake models and `test_ac03_*.py` in Sprint 3. |
| **AC-04: Pre-Auth Lifecycle & Reason Codes** | Brief Sec 5.1 | SCAFFOLDED | `specs/pre_auth_spec.md`, `specs/adjudication_spec.md` | No state transition logic or policy reason code mappings implemented. | Implement pre-auth transition engine and `test_ac04_*.py` in Sprint 3. |
| **AC-05: Auto-Approval Rule Engine** | Brief Sec 5.1 | SCAFFOLDED | `specs/pre_auth_spec.md`, `.claude/skills/pre-auth-auto-decider/SKILL.md` | Rule logic not implemented in production code. | Generate `src/domain/pre_auth_rule.py` and `test_ac05_*.py` in Sprint 3. |
| **AC-06: Post-Admission & Bill Buffer Cap** | Brief Sec 5.1 | SCAFFOLDED | `specs/admission_spec.md`, `specs/settlement_spec.md` | Buffer validation not implemented in application code. | Generate bill submission endpoint and `test_ac06_*.py` in Sprint 4. |
| **AC-07: Settlement Formula & Non-Negative Invariant** | Brief Sec 5.1 | SCAFFOLDED | `specs/settlement_spec.md` (v1.1.0), `docs/tdd.md` | Centralized `src/domain/settlement_rule.py` not yet generated. | Generate domain rule using Decimal and `test_ac07_*.py` in Sprint 5. |
| **AC-08: Claim State Machine Progression** | Brief Sec 5.1 | SCAFFOLDED | `specs/admission_spec.md`, `.claude/skills/state-machine-validator/SKILL.md` | `InvalidClaimStateException` not implemented. | Generate `src/domain/claim_state_rule.py` and `test_ac08_*.py` in Sprint 4. |
| **AC-09: Stubbed Notifications & Timeline View** | Brief Sec 5.1 | SCAFFOLDED | `specs/admission_spec.md`, `specs/app_spec.md` | Event bus notification stub and timeline API not generated. | Implement notification dispatcher and `test_ac09_*.py` in Sprint 4. |
| **AC-10: Insurer Admin Override & Audit** | Brief Sec 5.1 | SCAFFOLDED | `specs/adjudication_spec.md`, `.claude/agents/adjudicator-agent.md` | Override endpoint and audit capture not implemented. | Implement override action, role check, and `test_ac10_*.py` in Sprint 3. |
| **NFR-01: Fixed-Point Decimal Arithmetic** | Brief Sec 5.2 | VERIFIED | `.claude/hooks/settlement-cap-check.ps1/.sh`, `CLAUDE.md` | Hook verified active; production code not yet written. | Enforce in all generated monetary models in Sprints 2–5. |
| **NFR-02: Append-Only Persistence** | Brief Sec 5.2 | SCAFFOLDED | `specs/app_spec.md`, `src/repositories/CLAUDE.md` | Database schemas and repositories not yet created. | Generate insert-only SQLAlchemy models in Sprints 2–5. |
| **NFR-03: Zero PHI in Plaintext Logs** | Brief Sec 5.2 | VERIFIED | `.claude/hooks/phi-redaction-check.ps1/.sh`, `CLAUDE.md` | Hook verified active; logger utility not yet generated. | Implement `src/utils/logger.py` with masking interceptor in Sprint 7. |
| **NFR-04: Role Separation & Hospital Isolation** | Brief Sec 5.2 | VERIFIED | `.claude/hooks/role-boundary-check.ps1/.sh`, `src/controllers/CLAUDE.md` | Hook verified active; controller middleware not yet generated. | Implement role verification decorators in Sprint 2. |
| **NFR-05: Append-Only DB Migrations** | Brief Sec 5.2 | SCAFFOLDED | `src/repositories/CLAUDE.md` | No database migrations exist. | Initialize forward-only migrations in Sprint 2. |
| **NFR-06: Structured JSON Logging** | Brief Sec 5.2 | SCAFFOLDED | `CLAUDE.md`, `docs/architecture.md` | Logger module not yet implemented. | Implement JSON logger in `src/utils/logger.py` in Sprint 7. |
| **NFR-07: Health Endpoint SLA (< 1s)** | Brief Sec 5.2 | SCAFFOLDED | `specs/app_spec.md`, `docs/architecture.md` | `/health` route not yet implemented. | Implement `/health` route in FastAPI root in Sprint 2. |
| **NFR-08: Architecture Rules as Tests** | Brief Sec 5.2 | SCAFFOLDED | `tests/CLAUDE.md`, `docs/architecture.md` | `tests/architecture/` directory empty (0 tests). | Generate 3 structural test files in Sprint 7. |
| **Claude Harness Engine Foundation** | Brief Sec 7 | VERIFIED | Cloned to `C:\Users\Admin\claude-harness-engine`, configured in `~/.claude/settings.json` | Local Claude Code CLI not globally installed in PATH. | Available as permanent marketplace plugin for Claude Code. |
| **Project-Specific Agents (≥ 3)** | Brief Sec 7.1 | VERIFIED | 7 fully detailed agent files in `.claude/agents/` | None. | Agents ready for task dispatch. |
| **Project-Specific Skills (≥ 3)** | Brief Sec 7.1 | VERIFIED | 7 skill definitions in `.claude/skills/` | None. | Skills ready for invocation. |
| **Project-Specific Commands (≥ 2)** | Brief Sec 7.1 | VERIFIED | 5 custom commands in `.claude/commands/` | None. | Commands ready for invocation. |
| **Project-Specific Hooks (≥ 2)** | Brief Sec 7.1 | VERIFIED | 4 dual-mode hooks (.sh and .ps1) in `.claude/hooks/` | None. | Hooks tested and passing. |
| **Layered CLAUDE.md Hierarchy** | Brief Sec 7.1 | COMPLETE | Root `CLAUDE.md`, `AGENTS.md`, 6 module CLAUDE.md files | None. | Complete hierarchy established. |
| **Project Plugin Packaging** | Brief Sec 7.1 | COMPLETE | Root `plugin.json` referencing all MediCard substrate | None. | Substrate packaged. |
| **Playwright MCP Configuration** | Brief Sec 7.1 | CONFIGURED | `.mcp.json` configures Playwright MCP server | Evaluator has not yet invoked Playwright tests. | Execute in Sprint 6 UI testing. |
| **Programmatic Claude Agent SDK** | Brief Sec 7.1 | VERIFIED | `scripts/run_feature_agent.py` imports `anthropic` v1.11.0 | Requires live `ANTHROPIC_API_KEY` for non-dry-run LLM calls. | Safe mode active; dispatch evidence recorded. |
| **Business Case Document** | Brief Sec 7.2 | COMPLETE | `docs/business-case.md` | None. | Ready for reviewer plugin. |
| **Domain Rule Files (≥ 4)** | Brief Sec 7.2 | SCAFFOLDED | Target files specified in `specs/` | `src/domain/` currently empty (0 production files). | Generate domain rule modules in Sprints 2–5. |
| **Frontend Implementation** | Brief Sec 7.2 | SCAFFOLDED | `frontend/CLAUDE.md`, UI specifications | `frontend/` currently empty (0 LOC). | Generate responsive multi-party UI in Sprint 6. |
| **Architecture Tests (≥ 3)** | Brief Sec 7.3 | SCAFFOLDED | `tests/architecture/` directory created | 0 test files present. | Author 3 AST-based structural tests in Sprint 7. |
| **TDD Discipline Document** | Brief Sec 7.3 | COMPLETE | `docs/tdd.md` with AC-07 worked example | None. | Complete. |
| **3,000 Meaningful Code LOC** | Brief Sec 7.4 | MISSING | Current application LOC = 0 | 3,000 LOC deficit across `src/`, `frontend/`, `tests/`. | Generated during Sprints 2–7. |
| **Playwright UI Tests & Snapshots** | Brief Sec 7.4 | MISSING | None | No tests or snapshot directory present. | Generate Playwright tests and snapshots in Sprint 6. |
| **Unit Tests (≥ 20 Tests)** | Brief Sec 7.4 | MISSING | Current test count = 0 | 20+ test deficit. | Generate AC-tagged tests across Sprints 2–7. |
| **Coverage Artifact (`coverage.xml`)** | Brief Sec 7.4 | MISSING | None | `coverage.xml` absent. | Run `pytest --cov` in Sprint 8. |
| **GitLab CI Pipeline** | Brief Sec 7.5 | CONFIGURED | `.gitlab-ci.yml` with all required stages | Pipeline not executed on live remote runner. | Execute upon remote GitLab push in Sprint 8. |
| **PR-Driven Merges (≥ 3)** | Brief Sec 7.5 | PARTIAL | 1 local non-fast-forward merge preserved (`64ba2ee`) | 2 additional PR merges required; no remote configured. | Complete PR #2, #3, #4 in implementation sprints. |
| **Evidence Trail** | Brief Sec 8.1 | PARTIAL | `sprint-contracts/sprint-0-contract.md`, `specs/reviews/dispatch_ac-07.json` | Post-mortems and fix-loops empty (no runtime failures yet). | Record traces in `docs/post-mortems/` and `docs/fix-loops/`. |
