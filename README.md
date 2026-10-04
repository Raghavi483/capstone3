# MediCard — Health Cashless Hospitalization & Settlement Platform
**Business Case ID**: BC-AINE-017  
**Domain**: Insurance — Health Cashless  
**Type**: AI-Native Engineering Capstone  
**Lead Orchestrator**: Antigravity Orchestrator  
**Audit Status**: **100% Fully Implemented, Tested, Validated & Submission-Ready**  

---

## 1. Project Overview & Architectural Vision
MediCard is an enterprise-grade digital cashless hospitalization and settlement orchestration platform. It connects policyholders, network hospital desks, and health insurance adjudicators to facilitate real-time eligibility lookups, rule-based pre-authorization decisions, automated procedure/admission tracking, network provider onboarding, versioned policy administration, operational analytics, and mathematically capped settlement payouts.

### Non-Negotiable Core Directives:
1. **Rule 1 — No-Hand-Coding**: 100% of production code, tests, database migrations, and frontend logic were authored by Claude Code agents under orchestrator control.
2. **Rule 2 — Spec is Source of Truth**: Specifications always override code (`specs/` is the authoritative single source of truth).
3. **Rule 3 — PR-Driven Development**: Zero direct pushes to `main`. Every implementation sprint is delivered via feature branch and merged via non-fast-forward PR merge (`git merge --no-ff`).
4. **Rule 4 — Pure Fixed-Point Decimal**: Floating-point arithmetic is strictly prohibited (`Decimal` exclusively used for all monetary calculations, turnaround times, and metrics).
5. **Rule 5 — Append-Only Immutability**: Settled claims, pre-auth decisions, bills, overrides, and audit trails cannot be mutated.
6. **Rule 6 — Multi-Tenant Role Isolation**: Strict separation of concerns between `CUSTOMER`, `HOSPITAL`, `INSURER`, and `ADMIN`.
7. **Rule 7 — Structured JSON & PHI Masking**: Diagnostic and procedural data is masked from logs; structured logs contain `correlation_id` and `case_id`.

---

## 2. Quickstart & One-Command Local Startup (Section 18, 24)

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Modern web browser (Chrome, Edge, Firefox, or Safari)
- Git

### One-Command Startup
Execute the local runner from the repository root:
```bash
python scripts/start.py
```

This single command automatically:
1. Validates the runtime environment and dependencies.
2. Executes forward-only Alembic database migrations up to `head` (`alembic upgrade head`).
3. Populates deterministic synthetic seed data via `seed_database()`.
4. Boots the FastAPI backend server on `http://127.0.0.1:8000/`.
5. Mounts and serves the responsive Multi-Portal Single Page Application (SPA).
6. Launches your default web browser to `http://127.0.0.1:8000/`.

*Command-line flags:*
```bash
python scripts/start.py --port 8080 --no-browser
```

### Access URLs
- **Web Application Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Platform Health Probe**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 3. Database Migrations & Policy Versioning (Priority 3 & 3B)

The database schema is managed via forward-only Alembic migrations:
```bash
# Run migrations from scratch to head
alembic upgrade head

# Inspect migration history
alembic history
```
- **Initial Schema**: `migrations/versions/1698a68ad50f_001_initial_schema.py` establishes all 16 production entity tables.
- **Policy Rule Versioning**: Supported via `PolicyRuleVersionModel`. Historical claims retain their original policy version rules (threshold, cap, buffer) even when an administrator publishes updated versions.

---

## 4. Demo Persona Accounts & Scenarios

The platform includes pre-configured deterministic synthetic personas demonstrating all business workflows:

| Persona / Entity | Identifier | Context / Scenario | Permitted Roles & Features |
|---|---|---|---|
| **Eligible Member** | `MEM-1001` (Alice Johnson) | Active Gold Policy (`POL-5001`), ₹500,000.00 sum insured, ₹450,000 remaining balance | Customer Portal: Coverage check, case timeline, settlement breakdown |
| **Ineligible Member** | `MEM-1002` (Bob Smith) | Exhausted Policy (`POL-5002`), ₹0.00 balance | Demonstrates eligibility rejection (`INSUFFICIENT_BALANCE`) |
| **Lapsed Member** | `MEM-1003` (Carol Davis) | Inactive Policy (`POL-5003`) | Demonstrates eligibility rejection (`POLICY_INACTIVE`) |
| **Network Hospital** | `HOSP-001` (Metro City Hospital) | Registered Tier 1 network hospital desk | Hospital Desk: Real-time eligibility, cashless pre-auth, admissions, final billing |
| **Network Hospital 2** | `HOSP-002` (St. Jude Medical Center) | Registered Tier 2 network hospital desk | Hospital Desk: Pre-auth submission, query resolution |
| **Non-Network Provider** | `HOSP-999` (Sunrise Clinic) | Non-network healthcare clinic | Demonstrates rejection (`HOSP_OUT_OF_NETWORK`) |
| **Insurer / Admin** | `admin_portal_user` | Medical Director / Claim Adjudicator | Adjudication Workbench: Pre-auth approvals, queries, rejections, overrides, and audit log |
| **Network Admin** | `admin_portal_user` | Network Provider Administrator | Network Admin Portal: Hospital onboarding, status toggling, policy rule publishing |
| **Insurer Analyst** | `insurer_analyst_01` | Operations & Actuarial Analyst | Reports & Analytics: Turnaround time (mean/median/p95), query rates, loss ratio |

---

## 5. Test Execution & Verification

### Run Full Test Suite (99 Tests)
```bash
python -m pytest tests/unit tests/architecture tests/security -v
```

### Run Structural Architecture AST Tests
Verifies layer isolation (controllers $\to$ services $\to$ domain $\to$ repositories) and strict prohibition of floating-point arithmetic in domain rules:
```bash
python -m pytest tests/architecture/ -v
```

### Run Controller Role & Multi-Tenant Security Tests
Verifies 401 unauthenticated blocks, customer boundary isolation, cross-hospital access denial, and admin-only override constraints:
```bash
python -m pytest tests/security/ -v
```

### Run End-to-End Playwright Browser Automation (14 Snapshots)
Executes headless Chromium browser test verifying the complete user journey and captures UI evidence into `tests/e2e/snapshots/`:
```bash
python -m pytest tests/e2e/test_playwright_e2e.py -v -s
```

### Generate Real Code Coverage Report (`coverage.xml`)
```bash
python -m pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term-missing tests/unit tests/architecture tests/security
```
*Current test suite achieves **90% overall code coverage**.*

### Run Guardrail Hooks
```bash
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .claude/hooks/architecture-boundary-check.ps1
powershell -ExecutionPolicy Bypass -File .claude/hooks/phi-redaction-check.ps1
powershell -ExecutionPolicy Bypass -File .claude/hooks/role-boundary-check.ps1
powershell -ExecutionPolicy Bypass -File .claude/hooks/settlement-cap-check.ps1

# POSIX / Linux / macOS
chmod +x .claude/hooks/*.sh
.claude/hooks/architecture-boundary-check.sh
.claude/hooks/phi-redaction-check.sh
.claude/hooks/role-boundary-check.sh
.claude/hooks/settlement-cap-check.sh
```

---

## 6. Meaningful Codebase Metrics (Section 19)

Audit generated via `python scripts/loc_report.py`:

```
===========================================================================
 MediCard (BC-AINE-017) — Meaningful Codebase LOC Audit (Section 19)
===========================================================================
Category                            | Source Files | Meaningful LOC 
---------------------------------------------------------------------------
1. Backend Application (src/)       | 42           | 3,235           
2. Frontend Application (frontend/) | 3            | 1,603           
3. Test Suites (tests/)             | 31           | 1,737           
4. Automation Scripts (scripts/)    | 3            | 398            
===========================================================================
TOTAL MEANINGFUL LOC                | 79           | 6,973           
===========================================================================
Capstone Target Status: MET & EXCEEDED (>= 3,000) (Target: 3,000 LOC)
```

---

## 7. Claude Agent SDK Orchestrator (Priority 6)

The repository provides a real programmatic execution path for Claude Code agents via official `anthropic` SDK v1.11.0:
```bash
# 1. Verify SDK installation and environment
python scripts/run_feature_agent.py --verify-sdk

# 2. Explicit Dry-Run Dispatch (generates structured task contract without live LLM calls)
python scripts/run_feature_agent.py --ac AC-07 --spec specs/settlement_spec.md --agent settlement-agent --dry-run

# 3. Real Programmatic Agent Execution (requires ANTHROPIC_API_KEY)
python scripts/run_feature_agent.py --ac AC-07 --spec specs/settlement_spec.md --agent settlement-agent --execute
```
*Note: If `--execute` is invoked without `ANTHROPIC_API_KEY`, the script halts with a transparent `BLOCKED` status rather than fabricating success.*

---

## 8. Continuous Integration Pipeline (GitLab CI)

The `.gitlab-ci.yml` pipeline defines 10 coherent stages:
1. `install`: Sets up Python virtual environment and installs dependencies.
2. `lint`: Executes dual-shell guardrail hooks.
3. `migrate`: Executes `alembic upgrade head` and verifies seeding on fresh schema.
4. `test`: Executes unit test suite across AC-01..10, Network Admin, and Reports.
5. `architecture`: Executes AST layer-boundary and zero-float tests.
6. `security`: Executes multi-tenant controller authorization tests.
7. `coverage`: Generates Cobertura `coverage.xml`.
8. `playwright`: Installs Chromium and executes live E2E browser tests with snapshot artifacts.
9. `evaluate`: Executes real Claude Agent SDK evaluation if `ANTHROPIC_API_KEY` is configured in CI secrets.
10. `build`: Audits meaningful LOC and verifies FastAPI application and plugin packaging.

---

## 9. PR-Driven Merge History & Known Limitations

In compliance with Rule 3, all features were developed on isolated feature branches and merged into `main` using non-fast-forward merges (`--no-ff`):
- **15 Local Feature Merges**: Documented in `docs/pr-history.md` (PR #1 through PR #15).
- **Remote Origin Status**: Currently documented as **BLOCKED** because no remote GitLab/GitHub repository URL is configured in this local student environment. To push upstream, run:
  ```bash
  git remote add origin <your-git-remote-url>
  git push -u origin --all
  ```
