# MediCard — Harness Sprint & Ratcheting Verification Report
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Audit Date**: 2026-10-05  
**Workflow**: Generator → Evaluator → Ratcheting (Fix-Loop) → PR Merge  
**Status**: **PASS**  

---

## 1. Harness Engine Workflow Architecture

The AI-Native Harness Engine enforces continuous, contract-governed feature delivery through four distinct phases:
1. **Sprint Contract**: Defines strict acceptance criteria, non-functional requirements, input specifications, and verification commands before coding begins.
2. **Generator Execution**: Specialized Claude Code agent (e.g. `settlement-agent`, `eligibility-agent`, `generator.md`) generates TDD tests and domain implementations following the no-hand-coding rule.
3. **Evaluator Execution**: Independent `evaluator.md` agent audits code, runs test suites, checks architecture boundaries, and verifies invariants.
4. **Ratcheting & Fix-Loop**: Failures or edge cases trigger formal root-cause analysis, a targeted remediation diff, and regression re-evaluation.
5. **PR/Branch Evidence**: Non-fast-forward merge commit (`git merge --no-ff`) binds the verified sprint branch into `main`.

---

## 2. Complete End-to-End Sprint Evidence Chain: Sprint 12

### Phase 1: Sprint Contract
- **Contract File**: [sprint-contracts/sprint-12-contract.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/sprint-contracts/sprint-12-contract.md)
- **Target Invariants**:
  - Full Playwright E2E browser automation across all 14 lifecycle stages.
  - Programmatic Claude Agent SDK integration in `scripts/run_feature_agent.py` using official `anthropic` SDK v1.11.0.
  - Strict distinction between `--dry-run` and `--execute`.

### Phase 2: Generator Execution
- **Feature Branch**: `feat/sprint-12-playwright-and-sdk`
- **Assigned Agents**: `generator.md`, `ui-designer.md`, `test-engineer.md`
- **Generated Code Changes**:
  - Implemented dynamic Network Hospital Onboarding and Operational Reports tabs in `frontend/index.html` and `frontend/app.js`.
  - Added real `anthropic` SDK runner in `scripts/run_feature_agent.py` with controlled tools schemas (`read_specification_section`, `run_pytest_suite`, `record_audit_evidence`).
  - Added unit test suite `tests/unit/test_feature_agent_runner.py`.

### Phase 3: Initial Evaluator Execution & Detected Issue
- **Evaluator Agent**: `evaluator.md`
- **Initial Verification Result**:
  - Unit tests passed, but Playwright E2E browser test crashed during Step 13 (Network Onboarding) due to an invalid form submission event and URL prefix mismatch.
- **Ratcheting Trigger**: Detected defect documented in [docs/fix-loops/fix-loop-02-playwright-state-validation-onboarding.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/fix-loops/fix-loop-02-playwright-state-validation-onboarding.md).

### Phase 4: Ratcheting & Fix-Loop Remediation
- **Root Cause**: The Onboard Hospital form in `frontend/app.js` omitted required CORS headers and used inconsistent selector `#btn-onboard-hospital`.
- **Remediation**:
  - Fixed form action handler in `frontend/app.js` to dispatch JSON POST with `Content-Type: application/json` and `x-role: ADMIN`.
  - Added explicit waiting assertions in `tests/e2e/test_playwright_e2e.py` for selector `#onboard-feedback`.
- **Fix Verification**: Re-executed Playwright E2E runner: all 14 stages passed and 14 snapshots captured.

### Phase 5: Re-Evaluation & Verdict
- **Evaluator Report**: [specs/reviews/sprint-12-evaluator.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/reviews/sprint-12-evaluator.md)
- **Verdict**: **PASS** (100% test pass rate, 14 visual snapshots verified, `--verify-sdk` confirmed).

### Phase 6: PR Merge Evidence
- **Merge Commit**: `40c4e7f`
- **Commit Message**: `Merge pull request #14 from feat/sprint-12-playwright-and-sdk - Priority 5 & 6: Playwright Reproducibility & Real Claude Agent SDK`
- **Branch Graph**:
  ```text
  *   40c4e7f Merge pull request #14 from feat/sprint-12-playwright-and-sdk
  |\  
  | * dd8c5de feat(sprint-12): extend Playwright E2E with network admin & reports, implement real Claude Agent SDK runner, and add fix-loop
  |/
  ```

---

## 3. Second End-to-End Sprint Evidence Chain: Sprint 3

### Phase 1: Sprint Contract
- **Contract File**: [sprint-contracts/sprint-3-contract.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/sprint-contracts/sprint-3-contract.md) (Admission, Bill Buffer, State Machine, Timeline).
### Phase 2: Generator Execution
- **Feature Branch**: `feat/sprint-3-admission`
### Phase 3: Detected Failure & Root Cause
- **Incident**: `TypeError: Object of type Decimal is not JSON serializable` during discharge bill submission.
- **Post-Mortem / Fix-Loop**: [docs/fix-loops/fix-loop-01-decimal-json-serialization.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/fix-loops/fix-loop-01-decimal-json-serialization.md) and [docs/post-mortems/post-mortem-01-decimal-serialization.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/post-mortems/post-mortem-01-decimal-serialization.md).
### Phase 4: Ratcheting Fix
- Updated `json.dumps(..., default=str)` in `ClaimRepository.save_final_bill`.
### Phase 5: Evaluator Report
- [specs/reviews/sprint-3-evaluator.md](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/reviews/sprint-3-evaluator.md) (**PASS**).
### Phase 6: PR Merge
- Merge commit: `e48f42f` (`Merge PR #4: feat/sprint-3-admission`).
