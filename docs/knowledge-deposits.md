# Knowledge Deposits & Architecture Invariant Registry
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Purpose**: Continuous capture of engineering learnings, anti-patterns, and their permanent codification into automated hooks, skills, and agent rules.

---

## 1. Overview

In an AI-native engineering lifecycle, errors must never be manually patched and forgotten. When a pattern breaks or an agent produces suboptimal code, the root cause is extracted into a **Knowledge Deposit** and permanently enforced via:
- Git hooks (`.claude/hooks/`)
- Agent skills (`.claude/skills/`)
- Layered instructions (`CLAUDE.md`)
- Architecture test assertions (`tests/architecture/`)

---

## 2. Knowledge Deposits Log

### Deposit KD-001: Floating-Point Precision Leakage in Monetary Calculations
- **Category**: Financial Invariant & Precision (NFR-01)
- **Observed Risk**: Language models frequently default to `float` or standard numeric casting (`float(val)`) when performing arithmetic, introducing binary floating-point representation drift (e.g. `0.1 + 0.2 != 0.3`).
- **Codification**:
  1. Permanent domain rule: All currency values must instantiate `decimal.Decimal`.
  2. Created automated hook `.claude/hooks/settlement-cap-check.ps1` and `.sh` that inspects files in `src/domain/` and rejects any commit containing `float(` or `FLOAT` in monetary schemas.
  3. Added explicit instruction in root `CLAUDE.md`.

### Deposit KD-002: Accidental PHI Logging in Audit & Debug Statements
- **Category**: Data Privacy & Regulatory Compliance (NFR-03)
- **Observed Risk**: Agents generating log statements often include input payloads directly: `logger.info(f"Processing preauth: {request.dict()}")`, inadvertently logging patient clinical diagnosis, procedure details, or medical history.
- **Codification**:
  1. Mandated structured JSON logging with a field-level masking interceptor.
  2. Created hook `.claude/hooks/phi-redaction-check.ps1` and `.sh` that searches git diffs for sensitive keyword logging (`diagnosis`, `procedure`, `health_history`, `icd10`).
  3. Codified into `tests/architecture/test_phi_redaction.py`.

### Deposit KD-003: Bypass of Settlement Buffer Percentage Invariant
- **Category**: Business Rule Integrity (AC-06, AC-07)
- **Observed Risk**: Developers/agents occasionally apply deductible and co-pay directly to the raw final bill without first calculating `min(final_bill, pre_auth_amount + buffer)`. This allows hospital billing inflation beyond authorized caps.
- **Codification**:
  1. Centralized formula in `src/domain/settlement_rule.py`. Direct calculation in controllers or services is prohibited.
  2. Architecture test `test_layer_dependencies.py` fails if settlement math is imported or implemented outside `src/domain/settlement_rule.py`.
  3. Codified in `.claude/skills/settlement-calculator/SKILL.md`.

### Deposit KD-004: Direct Commits Bypassing PR Workflow
- **Category**: AI-Native Governance & Rule 3 (PR-Driven Development)
- **Observed Risk**: Unsupervised execution committing directly to `main` branch, destroying agent review traceability and PR evidence trails.
- **Codification**:
  1. Configured git pre-commit hook preventing direct commits to `main`.
  2. All work branches must match `feat/*` or `fix/*`.
  3. Merges require explicit `git merge --no-ff`.

### Deposit KD-005: Out-of-Sequence Claim State Transitions
- **Category**: State Machine Rigidity (AC-08)
- **Observed Risk**: Premature settlement requests before a patient is marked as `DISCHARGED`, or hospital admission updates without an approved pre-authorization.
- **Codification**:
  1. Domain module `claim_state_rule.py` enforces a deterministic state transition matrix.
  2. Any invalid transition raises `InvalidClaimStateException`.
  3. Codified in `.claude/skills/state-machine-validator/SKILL.md`.
