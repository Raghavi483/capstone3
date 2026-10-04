# Repository Assessment & Baseline Inventory
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform  
**Business Case ID**: BC-AINE-017  
**Domain**: Insurance — Health Cashless  
**Assessment Date**: 2026-10-04  
**Author**: Lead AI-Native Engineering Orchestrator  

---

## 1. Executive Summary

This assessment audits the initial state of the `capstone3` workspace prior to any application code generation. In compliance with **Section 10 & 41** of the capstone brief, this document catalogs existing repository structure, evaluates the baseline Claude Harness Engine foundation, conducts an exhaustive gap analysis against all 10 Functional Acceptance Criteria (AC-01 to AC-10), 8 Non-Functional Requirements (NFR-01 to NFR-08), and the 5 evaluation rubric categories (AI-native engineering practices, business understanding, architectural discipline, technical implementation, and CI/CD).

---

## 2. Existing Repository Structure

Prior to orchestrator initialization, the workspace was a completely fresh, empty directory (`c:\Users\Admin\OneDrive\Desktop\capstone3`).

- **Git Version**: 2.55.0.windows.5
- **Git Repository State**: Initialized empty git repository with branch `main`, author `Raghavi483` (`raghaviperiyasamy48@gmail.com`).
- **Installed Runtimes**:
  - Python 3.12.1
  - Node.js v20.10.0 / npm 10.8.2
  - Playwright MCP / Claude SDK capable runtimes
- **Existing Code/Files**: None (greenfield workspace).
- **Harness State**: The Claude Harness Engine plugin was not previously cloned or extracted into this workspace.

---

## 3. Claude Harness Foundation Assessment

The capstone specification states:
> *"Install the Claude Harness Engine plugin first. The harness ships 7 base agents (planner, generator, evaluator, security-reviewer, test-engineer, design-critic, ui-designer), 12+ hooks, base commands, sprint contracts, an evaluator wired to Playwright MCP, and a self-healing loop."*

### Current Harness Inventory & Findings:
| Component | Expected Base | Current Workspace State | Action Required |
| :--- | :--- | :--- | :--- |
| **Base Agents** | 7 (planner, generator/implementer, evaluator/reviewer, security-reviewer, test-engineer/tester, design-critic, ui-designer) | Absent | Scaffold all 7 base agents under `.claude/agents/` |
| **Base Hooks** | 12+ hooks (pre-commit, lint, no-hand-coding, etc.) | Absent | Implement core guardrail hooks under `.claude/hooks/` |
| **Base Commands** | Standard workflow commands | Absent | Scaffold base commands under `.claude/commands/` |
| **Harness Plugin Manifest** | Harness `plugin.json` | Absent | Scaffold harness configuration |
| **MCP Configuration** | `.mcp.json` with Playwright MCP | Absent | Create `.mcp.json` targeting Playwright MCP |
| **Sprint Contracts** | `sprint-contracts/` directory & templates | Absent | Establish sprint contract framework |
| **Evaluator Outputs** | `specs/reviews/` | Absent | Create directory structure for evaluator reviews |

---

## 4. Comprehensive Gap Analysis Against MediCard Brief

### 4.1 Functional Acceptance Criteria (AC-01 through AC-10)
| ID | Requirement Summary | Workspace State | Gap / Planned Delivery |
| :--- | :--- | :--- | :--- |
| **AC-01** | Customer registration & health policy linking; coverage details (sum insured, exclusions, network hospitals) | Not Implemented | `specs/eligibility_spec.md`, `specs/network_admin_spec.md`, Sprint 2 |
| **AC-02** | Network hospital eligibility lookup by `member_id` & `policy_id`; returns `ELIGIBLE` / `NOT_ELIGIBLE` with reason codes | Not Implemented | `specs/eligibility_spec.md`, domain validator `eligibility_rule.py`, Sprint 2 |
| **AC-03** | Hospital pre-auth submission (diagnosis, estimated_cost, expected admission date); initial state `PENDING` | Not Implemented | `specs/pre_auth_spec.md`, Sprint 3 |
| **AC-04** | Pre-auth lifecycle (`PENDING` → `APPROVED` / `PARTIALLY_APPROVED` / `REJECTED` / `QUERY_RAISED`) with policy reason codes | Not Implemented | `specs/pre_auth_spec.md`, `specs/adjudication_spec.md`, Sprint 3 |
| **AC-05** | Auto-approval engine: `estimated_cost <= threshold` AND `diagnosis in auto_approved_list` → auto-approved up to policy cap | Not Implemented | `specs/pre_auth_spec.md`, domain `pre_auth_rule.py`, Sprint 3 |
| **AC-06** | Post-admission procedure updates & final bill; bill cannot exceed `pre_auth_amount + buffer%` | Not Implemented | `specs/admission_spec.md`, Sprint 4 |
| **AC-07** | Settlement calculation: `min(final_bill, pre_auth + buffer) - deductible - co_pay`; invariant `settlement >= 0` | Not Implemented | `specs/settlement_spec.md`, domain `settlement_rule.py`, Sprint 5 |
| **AC-08** | Cashless claim state machine: `PRE_AUTH → ADMITTED → DISCHARGED → SETTLED / DISPUTED → CLOSED`; invalid transitions raise `InvalidClaimStateException` | Not Implemented | `specs/admission_spec.md`, domain `claim_state_rule.py`, Sprint 4 |
| **AC-09** | Stubbed notifications on transitions; customer & hospital timeline view | Not Implemented | `specs/app_spec.md`, services notification stub, Sprint 4 & 6 |
| **AC-10** | Insurer admin override for auto-rejected pre-auth / escalated query with reason, actor, timestamp; audited | Not Implemented | `specs/adjudication_spec.md`, domain `role_boundary_rule.py`, Sprint 3 & 5 |

### 4.2 Non-Functional Requirements (NFR-01 through NFR-08)
| ID | Requirement Summary | Workspace State | Gap / Planned Delivery |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Monetary calculations in fixed-point decimal (`Decimal`); strictly no floating-point | Not Implemented | Root `CLAUDE.md`, settlement domain rule, hook `settlement-cap-check` |
| **NFR-02** | Append-only ledger for decisions, bills, settlements, overrides | Not Implemented | Repository architecture, audit schema, append-only domain invariants |
| **NFR-03** | PHI redaction: diagnosis, procedures, health history never logged in plaintext | Not Implemented | Structured logger with PHI filter, hook `phi-redaction-check.sh` |
| **NFR-04** | Authentication & role separation (CUSTOMER, HOSPITAL, INSURER, ADMIN); hospital isolation | Not Implemented | Controller middleware, role boundary rule `role_boundary_rule.py` |
| **NFR-05** | Database and policy migrations are append-only | Not Implemented | Migration management discipline, versioned policy tables |
| **NFR-06** | Structured JSON logging with `request_id`, `correlation_id`, `case_id` | Not Implemented | Logging utility module in `src/utils/logger.py` |
| **NFR-07** | Health endpoint `/health` returning HTTP 200 within 1s | Not Implemented | FastAPI `/health` endpoint with liveness & readiness checks |
| **NFR-08** | Architectural rules enforced via automated tests (tests/architecture/) | Not Implemented | `tests/architecture/` with structural tests, layering validation |

### 4.3 AI-Native Engineering Substrate Requirements
| Substrate Component | Required by Brief | Status |
| :--- | :--- | :--- |
| **Layered CLAUDE.md Hierarchy** | Root `CLAUDE.md`, module/folder CLAUDE.md files, `AGENTS.md` as TOC | Establishing in Sprint 0 |
| **Project-Specific Agents** | ≥3 domain/technical agents under `.claude/agents/` | Adding: `eligibility-agent`, `pre-auth-decider-agent`, `settlement-agent`, `adjudicator-agent`, `state-machine-validator-agent`, `audit-tracer-agent`, `architecture-test-agent` |
| **Project-Specific Skills** | ≥3 skills under `.claude/skills/` | Adding: `eligibility-resolver`, `pre-auth-auto-decider`, `settlement-calculator`, `network-hospital-validator`, `state-machine-validator`, `audit-tracer`, `archtest-author` |
| **Project-Specific Commands** | ≥2 custom commands under `.claude/commands/` | Adding: `validate-medi-card.md`, `implement-feature.md`, `validate-ac.md`, `settlement-check.md`, `security-review.md` |
| **Project-Specific Hooks** | ≥2 hooks under `.claude/hooks/` | Adding: `phi-redaction-check.sh/.ps1`, `settlement-cap-check.sh/.ps1`, `role-boundary-check.sh/.ps1`, `architecture-boundary-check.sh/.ps1` |
| **Project Plugin Manifest** | `plugin.json` packaging MediCard substrate | Creating `plugin.json` at repository root |
| **MCP Configuration** | `.mcp.json` with Playwright MCP | Creating `.mcp.json` |
| **Programmatic Claude SDK** | At least one real script under `scripts/` | Creating `scripts/run_feature_agent.py` |
| **Architecture Documentation** | `docs/architecture.md` with Mermaid diagram | Creating layered architecture doc |
| **Business Case Document** | `docs/business-case.md` for evaluator plugin | Creating full business case |
| **TDD Documentation** | `docs/tdd.md` with worked example (AC-07) | Creating TDD doc |
| **Knowledge Deposit Log** | `docs/knowledge-deposits.md` | Creating knowledge deposit tracker |
| **CI/CD Configuration** | `.gitlab-ci.yml` with Claude Action | Creating `.gitlab-ci.yml` |

---

## 5. Potential Conflicts & Clarifications

1. **Operating System Environment**:
   - The brief references shell scripts (`.sh`). The active host OS is Windows with PowerShell.
   - *Resolution*: Hooks will be implemented as dual-mode scripts (both POSIX `.sh` for GitLab CI and PowerShell `.ps1` for local Windows developer execution), ensuring identical behavior across both environments.
2. **Harness Foundation Availability**:
   - Because the workspace is clean and does not inherit a pre-existing clone, the orchestrator scaffolds the entire canonical 7-agent Harness Engine alongside the MediCard extensions, ensuring 100% compliance with rubric expectations.
3. **No-Hand-Coding Boundary**:
   - Substrate files (specs, agent definitions, skills, hooks, commands, documentation, contracts, CI configuration) are explicitly permitted to be authored by the Orchestrator. Production application code, production tests, and seed data scripts will be generated exclusively by Claude Code agent tasks in subsequent sprints under PR-driven branches.

---

## 6. Risks & Mitigation Plan

| Risk | Severity | Mitigation |
| :--- | :--- | :--- |
| **Token Exhaustion on Claude Code Tasks** | HIGH | Implement Section 39 Token Optimization Strategy: split tasks into micro-units referencing exact AC IDs, specific files, and targeted test commands. |
| **Specification Drift** | HIGH | Enforce Rule 2: Spec is Source of Truth. If tests/code disagree, specification is reviewed first, updated if needed, and code regenerated. |
| **Accidental Direct Commits to Main** | CRITICAL | Enforce Rule 3: Git pre-commit and pre-push hooks blocking direct commits to `main`. All merges require PR branches and `git merge --no-ff`. |
| **PHI Leakage in JSON Logs** | HIGH | Hook `phi-redaction-check` and structured logging interceptor with strict field masking. |
| **Floating-Point Precision Errors** | HIGH | Hook `settlement-cap-check` scanning for `float` conversions in monetary paths; strict Python `Decimal` enforcement. |

---

## 7. Recommended Technology Stack

Based on available runtimes (Python 3.12.1, Node.js 20.10.0, npm 10.8.2) and the brief's preference for simplicity, reliability, and local testability:

- **Backend**: Python 3.12 + FastAPI (high performance, native async, strong typing with Pydantic v2, clean dependency injection)
- **Database**: SQLite with SQLAlchemy 2.0 ORM (zero-config, append-only audit ledger, in-memory test isolation)
- **Calculations**: Python standard library `decimal.Decimal` (fixed-point precision for NFR-01)
- **Unit & Integration Testing**: `pytest` + `pytest-cov` (AC-tagged tests, coverage reporting producing `coverage.xml`)
- **Architecture Enforcement**: Custom structural test suite in `tests/architecture/` validating clean layer boundaries
- **Frontend**: Modern responsive Single Page Application (HTML5 / Vanilla CSS / JavaScript or React) optimized for Playwright MCP testing
- **E2E / UI Testing**: Playwright MCP with snapshot directory
- **CI/CD**: `.gitlab-ci.yml` with test, coverage, lint, and Claude Code evaluation stages

---

## 8. Baseline Implementation Plan

The project will proceed across 9 disciplined sprints (Sprint 0 through Sprint 8):
- **Sprint 0**: Substrate Initialization, Harness Foundation, Specifications, Layered CLAUDE.md, Contracts
- **Sprint 1**: Business Case, Architecture Model, TDD Blueprint, Reviewer Alignment
- **Sprint 2**: Eligibility Engine & Network Hospital Admin (AC-01, AC-02)
- **Sprint 3**: Pre-Authorization Submission & Rule Decisioning (AC-03, AC-04, AC-05, AC-10)
- **Sprint 4**: Admission Tracking & Claim State Machine (AC-06, AC-08, AC-09)
- **Sprint 5**: Settlement Calculation & Immutable Audit Ledger (AC-07, NFR-01, NFR-02)
- **Sprint 6**: Multi-Party Frontend & Playwright Validation (Customer, Hospital, Insurer, Admin)
- **Sprint 7**: Reports Engine, Security Hardening & Architectural Tests (NFR-03, NFR-04, NFR-08)
- **Sprint 8**: CI/CD Integration, Coverage Verification & Final Evaluation Gate
