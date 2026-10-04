# MediCard Implementation Roadmap & Sprint Strategy
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform  
**Business Case**: BC-AINE-017  
**Strategy**: PR-Driven Development, Generator-Evaluator Loop, Zero Direct Commits to Main  

---

## 1. Overview & Operating Model

MediCard is delivered using an AI-native engineering discipline where the Lead Orchestrator oversees specification, architectural guardrails, and validation, while Claude Code agents execute discrete, AC-bounded implementation tasks.

Every implementation sprint adheres to the **PR-Driven Workflow**:
```
Feature Branch (e.g. feat/sprint-2-eligibility)
  ↓
Claude Code Task Dispatch (with explicit AC ID & Token Optimization)
  ↓
Agent Code & Test Generation
  ↓
Local Hook Validation (phi-redaction, settlement-cap, role-boundary)
  ↓
Automated Test & Architecture Review
  ↓
Pull Request Evaluation
  ↓
Merge to main via: git merge --no-ff
```

---

## 2. Sprint Roadmap & Scope Matrix

| Sprint | Focus & Scope | Target ACs & NFRs | Agent Responsible | Deliverables | Branch Name |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sprint 0** | AI-Native Substrate, Harness Foundation & Specs | Foundation, Section 7.1, 8.1 | Orchestrator + Planner | Specs, Agent definitions, Skills, Hooks, Commands, `plugin.json`, `.mcp.json`, Layered `CLAUDE.md`, Sprint 0 Contract | `feat/sprint-0-substrate` |
| **Sprint 1** | Business Context, Architecture Blueprint & TDD Design | NFR-08, Section 7.2, 7.3 | Orchestrator + Architect | `docs/business-case.md`, `docs/architecture.md`, `docs/tdd.md`, `docs/knowledge-deposits.md` | `feat/sprint-1-architecture` |
| **Sprint 2** | Customer Registration, Policy Linking & Hospital Eligibility | AC-01, AC-02, NFR-04 | `eligibility-agent` + `test-engineer` | Domain `eligibility_rule.py`, `network_hospital_rule.py`, services, repositories, tests (`test_ac01`, `test_ac02`) | `feat/sprint-2-eligibility` |
| **Sprint 3** | Pre-Authorization Engine, Auto-Approval & Adjudication Override | AC-03, AC-04, AC-05, AC-10 | `pre-auth-decider-agent` + `adjudicator-agent` | Domain `pre_auth_rule.py`, auto-approval engine, override audit, tests (`test_ac03`, `test_ac04`, `test_ac05`, `test_ac10`) | `feat/sprint-3-preauth` |
| **Sprint 4** | Admission Tracking, Procedure Updates & Claim State Machine | AC-06, AC-08, AC-09 | `state-machine-validator-agent` + `generator` | Domain `claim_state_rule.py`, procedure recording, transition event bus / stub notifications, tests (`test_ac06`, `test_ac08`, `test_ac09`) | `feat/sprint-4-admission` |
| **Sprint 5** | Settlement Calculation, Fixed-Point Decimal & Append-Only Audit | AC-07, NFR-01, NFR-02 | `settlement-agent` + `audit-tracer-agent` | Domain `settlement_rule.py`, settlement service, immutable audit ledger, tests (`test_ac07_settlement.py`) | `feat/sprint-5-settlement` |
| **Sprint 6** | Multi-Party Responsive UI & Playwright End-to-End Validation | AC-01 to AC-10 (UI Journeys) | `ui-designer` + `evaluator` | Responsive portal (Customer, Hospital, Adjudicator, Admin), Playwright tests, UI snapshot directory | `feat/sprint-6-frontend` |
| **Sprint 7** | Reports, Analytics, PHI Hardening & Architecture Tests | NFR-03, NFR-06, NFR-07, NFR-08 | `architecture-test-agent` + `security-reviewer` | Report endpoints, JSON logger, PHI scanner, `tests/architecture/` structural tests | `feat/sprint-7-reports-security` |
| **Sprint 8** | CI/CD Pipeline, Coverage XML & Final Assessment Gate | Rubric 100% Quality Gate | Orchestrator + Evaluator | `.gitlab-ci.yml`, Claude Code Action, `coverage.xml`, evidence trails, final post-mortem | `feat/sprint-8-cicd-final` |

---

## 3. Claude Code Token Optimization Strategy (Prompt Section 39)

To eliminate token waste and prevent agent hallucination or scope creep, Claude Code instructions MUST follow this strict template:

```markdown
### Task Specification
- **Feature**: [Feature Name]
- **Target AC**: [e.g. AC-07]
- **Specification Source**: [e.g. specs/settlement_spec.md#AC-07]
- **Target Files to Create/Update**:
  - `src/domain/settlement_rule.py`
  - `src/services/settlement_service.py`
  - `tests/unit/test_ac07_settlement.py`
- **Design Constraints**:
  - Use `decimal.Decimal` exclusively. Never cast monetary values to `float`.
  - Invariant: `settlement_amount >= 0`.
  - Apply buffer percentage check: `final_bill <= pre_auth_amount + buffer`.
- **Validation Command**:
  - `pytest tests/unit/test_ac07_settlement.py -v`
- **Acceptance Gate**:
  - All tests pass; no diff outside declared target files.
```

---

## 4. Quality Gate & Evidence Trail Checklist

Before any sprint branch is merged into `main`, the Evaluator verifies:
- [ ] Specification traceability verified (every commit references AC ID)
- [ ] No manual coding detected (all production code generated via agent tasks)
- [ ] Fixed-point decimal arithmetic verified for all currency paths
- [ ] PHI check hook passed (zero health data logged in plaintext)
- [ ] Architecture tests pass without boundary violations
- [ ] All unit and integration tests passing
- [ ] Pull request reviewed with non-fast-forward merge (`git merge --no-ff`)
