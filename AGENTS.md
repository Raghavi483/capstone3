# AGENTS.md — Agent & Substrate Table of Contents
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Role**: Central Navigation & Substrate Index  

---

## 1. Governance & Core Directives
- **Root Instructions**: [CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/CLAUDE.md) — Mandatory non-negotiable rules, invariants, and constraints.
- **Repository Assessment**: [docs/repository-assessment.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/repository-assessment.md) — Baseline audit and gap analysis.
- **Implementation Roadmap**: [docs/implementation-roadmap.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/implementation-roadmap.md) — Sprints, PR branches, and deliverable matrix.
- **Business Case**: [docs/business-case.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/business-case.md) — Business context, value proposition, and user journeys.
- **Architecture Blueprint**: [docs/architecture.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/architecture.md) — Layered architecture, Mermaid diagrams, and data flows.
- **TDD Blueprint**: [docs/tdd.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/tdd.md) — Red-Green-Refactor with AC-07 worked example.
- **Knowledge Deposits**: [docs/knowledge-deposits.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/knowledge-deposits.md) — Codified anti-patterns and learnings.

---

## 2. Specifications Index (`specs/`)
- **System Root Spec**: [specs/app_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- **Eligibility & Coverage (AC-01, AC-02)**: [specs/eligibility_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/eligibility_spec.md)
- **Pre-Authorization Engine (AC-03, AC-04, AC-05)**: [specs/pre_auth_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/pre_auth_spec.md)
- **Adjudication & Override (AC-04, AC-10)**: [specs/adjudication_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/adjudication_spec.md)
- **Admission & Claim State Machine (AC-06, AC-08, AC-09)**: [specs/admission_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/admission_spec.md)
- **Settlement Calculator (AC-07, NFR-01, NFR-02)**: [specs/settlement_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/settlement_spec.md)
- **Network Administration**: [specs/network_admin_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/network_admin_spec.md)
- **Reports & Analytics**: [specs/reports_spec.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/reports_spec.md)

---

## 3. Layered Instructions Hierarchy
- **Domain Layer Directives**: [src/domain/CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/src/domain/CLAUDE.md)
- **Service Layer Directives**: [src/services/CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/src/services/CLAUDE.md)
- **Controller Layer Directives**: [src/controllers/CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/src/controllers/CLAUDE.md)
- **Repository Layer Directives**: [src/repositories/CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/src/repositories/CLAUDE.md)
- **Testing Directives**: [tests/CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/tests/CLAUDE.md)
- **Frontend Directives**: [frontend/CLAUDE.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/frontend/CLAUDE.md)

---

## 4. Agent Roster (`.claude/agents/`)
### Harness Base Foundation:
1. `planner.md` — Strategic breakdown of user stories and architecture requirements.
2. `generator.md` / `implementer.md` — Autonomous code generator adhering to TDD.
3. `evaluator.md` / `reviewer.md` — Pull request and quality gate reviewer.
4. `security-reviewer.md` — Audits role boundaries, PHI redaction, and OWASP safety.
5. `test-engineer.md` / `tester.md` — Generates unit, integration, and architecture test suites.
6. `design-critic.md` — Evaluates user interface responsiveness and usability.
7. `ui-designer.md` — Builds frontend presentation components.

### MediCard Domain & Technical Agents:
8. `eligibility-agent.md` — Solves member eligibility, policy coverage, and network validation (AC-01, AC-02).
9. `pre-auth-decider-agent.md` — Evaluates rule auto-approval and policy cap logic (AC-03, AC-04, AC-05).
10. `settlement-agent.md` — Enforces decimal arithmetic, buffer percentages, and invariant checks (AC-07, NFR-01).
11. `adjudicator-agent.md` — Coordinates manual review queues and admin override verification (AC-10).
12. `state-machine-validator-agent.md` — Verifies strict claim progression and `InvalidClaimStateException` (AC-08).
13. `audit-tracer-agent.md` — Enforces append-only immutable audit ledger recording (NFR-02).
14. `architecture-test-agent.md` — Authors structural tests validating layer isolation (NFR-08).

---

## 5. Skills Directory (`.claude/skills/`)
- `.claude/skills/eligibility-resolver/SKILL.md` — Resolves member status, active dates, and network provider tiers.
- `.claude/skills/pre-auth-auto-decider/SKILL.md` — Evaluates auto-approval rules and policy caps.
- `.claude/skills/settlement-calculator/SKILL.md` — Centralized invariant-checked settlement calculation.
- `.claude/skills/network-hospital-validator/SKILL.md` — Validates hospital network registration.
- `.claude/skills/state-machine-validator/SKILL.md` — Validates state machine progression.
- `.claude/skills/audit-tracer/SKILL.md` — Constructs immutable audit records.
- `.claude/skills/archtest-author/SKILL.md` — Generates layer-boundary architecture tests.

---

## 6. Custom Commands (`.claude/commands/`)
- `.claude/commands/validate-medi-card.md` — Full platform validation (lint, tests, hooks, architecture).
- `.claude/commands/implement-feature.md` — Dispatches targeted Claude Code agent feature implementation.
- `.claude/commands/validate-ac.md` — Validates compliance for a specific Acceptance Criteria ID.
- `.claude/commands/settlement-check.md` — Runs settlement calculation edge cases and invariant verification.
- `.claude/commands/security-review.md` — Runs PHI redaction, auth boundaries, and role checks.

---

## 7. Guardrail Hooks (`.claude/hooks/`)
- `phi-redaction-check.ps1` / `.sh` — Prevents committing plaintext health diagnoses into logs.
- `settlement-cap-check.ps1` / `.sh` — Prevents floating-point usage or bypass of buffer limits.
- `role-boundary-check.ps1` / `.sh` — Scans for unauthenticated endpoints or hospital multi-tenancy breaches.
- `architecture-boundary-check.ps1` / `.sh` — Detects layer dependency violations.

---

## 8. Plugins & MCP
- `plugin.json` — MediCard substrate plugin packaging.
- `.mcp.json` — Playwright MCP configuration.
- `scripts/run_feature_agent.py` — Programmatic Claude Agent SDK runner.
