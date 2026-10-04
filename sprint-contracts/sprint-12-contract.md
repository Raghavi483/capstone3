# Sprint 12 Contract — Playwright Reproducibility & Real Claude Agent SDK
**Sprint**: Sprint 12 (Priority 5 & Priority 6, Section 9, Section 10)  
**Assigned Agents**: `test-engineer`, `evaluator`, `implementer`  
**Status**: **COMPLETED**  
**Date**: 2026-10-04  

---

## 1. Objectives
1. Extend Playwright E2E browser testing to cover real dynamic Network Administration and operational Reports & Analytics.
2. Execute live Playwright testing against Chromium and capture 14 distinct visual snapshots.
3. Review and upgrade `scripts/run_feature_agent.py` to support real Anthropic Agent SDK execution (`--execute`) alongside explicit dry-run mode (`--dry-run`).
4. Ensure real controlled tools schema, authentic client execution, and transparent BLOCKED reporting when API key is missing.
5. Author unit test suite for the feature agent runner (`tests/unit/test_feature_agent_runner.py`).

---

## 2. Invariants & Acceptance Gates
- Playwright E2E must execute live without errors and produce verified browser screenshots.
- Zero fake success claims: `--execute` without API key must return a non-zero exit code and state `BLOCKED`.
- Unit test suite must expand to 99 tests (94 previous + 5 agent runner tests) with 100% passing.
