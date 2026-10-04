# Sprint 0 Contract: AI-Native Substrate & Foundation Initialization
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Sprint**: Sprint 0  
**Phase**: Assessment, Substrate, Specification & Architecture Foundation  
**Sprint Status**: IN_PROGRESS  
**Lead Orchestrator**: Antigravity Orchestrator  
**Target Branch**: `feat/sprint-0-substrate`  

---

## 1. Objective
Establish the complete AI-native engineering substrate required by the MediCard capstone brief (Sections 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21), including:
- Repository assessment and gap analysis (`docs/repository-assessment.md`)
- Full specifications suite (`specs/app_spec.md` + 7 feature specs)
- Business case documentation (`docs/business-case.md`)
- Architecture blueprint with Mermaid diagrams (`docs/architecture.md`)
- TDD strategy and worked example (`docs/tdd.md`)
- Canonical 7-agent Harness Engine + MediCard domain/technical agents
- Project skills under `.claude/skills/`
- Custom commands under `.claude/commands/`
- Guardrail hooks under `.claude/hooks/`
- Packaging in `plugin.json` and `.mcp.json`
- Programmatic Claude Agent SDK runner in `scripts/run_feature_agent.py`
- Layered `CLAUDE.md` hierarchy and `AGENTS.md` navigation map

---

## 2. In-Scope Deliverables
1. `docs/repository-assessment.md` (Completed)
2. `docs/implementation-roadmap.md` (Completed)
3. `sprint-contracts/sprint-0-contract.md` (This document)
4. `docs/business-case.md`
5. `docs/architecture.md`
6. `docs/tdd.md`
7. `docs/knowledge-deposits.md`
8. `specs/app_spec.md`
9. `specs/eligibility_spec.md`
10. `specs/pre_auth_spec.md`
11. `specs/adjudication_spec.md`
12. `specs/admission_spec.md`
13. `specs/settlement_spec.md`
14. `specs/network_admin_spec.md`
15. `specs/reports_spec.md`
16. `.claude/agents/` (planner, generator, evaluator, security-reviewer, test-engineer, design-critic, ui-designer, eligibility-agent, pre-auth-decider-agent, settlement-agent, adjudicator-agent, state-machine-validator-agent, audit-tracer-agent, architecture-test-agent)
17. `.claude/skills/` (eligibility-resolver, pre-auth-auto-decider, settlement-calculator, network-hospital-validator, state-machine-validator, audit-tracer, archtest-author)
18. `.claude/commands/` (validate-medi-card, implement-feature, validate-ac, settlement-check, security-review)
19. `.claude/hooks/` (phi-redaction-check, settlement-cap-check, role-boundary-check, architecture-boundary-check)
20. `plugin.json` and `.mcp.json`
21. `scripts/run_feature_agent.py`
22. Layered `CLAUDE.md` (Root + `src/domain/CLAUDE.md`, `src/services/CLAUDE.md`, `src/controllers/CLAUDE.md`, `src/repositories/CLAUDE.md`, `tests/CLAUDE.md`, `frontend/CLAUDE.md`)
23. `AGENTS.md` Table of Contents
24. `.gitlab-ci.yml`

---

## 3. Out-of-Scope (Strict Non-Negotiable Rule)
- Writing production application code (`src/` implementation code)
- Writing production tests (`tests/` implementation tests)
- Running database migrations or application servers
*All application implementation is strictly deferred to Sprint 1+ under Claude Code agent generation.*

---

## 4. Acceptance Criteria for Sprint 0
- [ ] AC-S0-01: Repository assessment catalogs all requirements and verifies empty baseline.
- [ ] AC-S0-02: Business case document thoroughly covers problem statement, user journeys, success metrics, and domain rules.
- [ ] AC-S0-03: Root specification and 7 feature specifications are established with explicit AC-NN and Given-When-Then sections.
- [ ] AC-S0-04: Architecture document contains layered structure and at least one Mermaid diagram showing eligibility-to-settlement data flow.
- [ ] AC-S0-05: TDD document outlines Red-Green-Refactor with AC-07 worked example.
- [ ] AC-S0-06: All required agents, skills, hooks, and commands are instantiated and documented.
- [ ] AC-S0-07: `plugin.json` packages substrate; `.mcp.json` configures Playwright MCP.
- [ ] AC-S0-08: Programmatic Claude Agent SDK script is functional in `scripts/run_feature_agent.py`.
- [ ] AC-S0-09: Layered `CLAUDE.md` hierarchy and `AGENTS.md` TOC are established.
- [ ] AC-S0-10: Guardrail hooks are validated executable.

---

## 5. Review & Evaluator Gate
- **Evaluator**: Lead AI-Native Engineering Orchestrator
- **Exit Condition**: Complete substrate verified; git commit on `feat/sprint-0-substrate` merged to `main` via `--no-ff`.
