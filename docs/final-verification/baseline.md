# MediCard — Baseline Audit & System State
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Audit Date**: 2026-10-05  
**Stage**: Pre-Modification Baseline (Step 1)  

---

## 1. Environment & Runtime Specifications

| Property | Value | Notes |
|---|---|---|
| **Operating System** | Windows (win32) | Windows 11 / PowerShell environment |
| **Python Version** | `Python 3.12.1` | Global runtime `C:\Python312\python.exe` |
| **Pytest Version** | `pytest-9.1.1` | Plugins: `anyio-4.15.1`, `langsmith-0.12.2`, `cov-7.1.0` |
| **Coverage Tool** | `pytest-cov 7.1.0` | Cobertura XML and terminal reporting |
| **Playwright Version** | `playwright 1.63.0` | Chromium headless automation enabled |
| **Anthropic SDK** | `anthropic 1.11.0` | Location: `C:\Users\Admin\AppData\Roaming\Python\Python312\site-packages` |
| **Dependency Manifest** | **MISSING** (No `requirements.txt` or `pyproject.toml`) | **Primary Blocker for clean environment reproducibility** |
| **Git Working Tree** | Clean (`main` branch) | Commit: `feb65a1` |
| **Git Remotes** | None configured (`git remote -v` returns empty) | Remote push blocked until user configures remote URL |

---

## 2. Baseline Test Suite Execution

### Minimum Mandated Test Suite
**Command**:
```powershell
python -m pytest tests/unit tests/architecture tests/security -q
```

**Actual Execution Output**:
```
........................................................................ [ 72%]
...........................                                              [100%]
============================== warnings summary ===============================
..\..\..\AppData\Roaming\Python\Python312\site-packages\starlette\testclient.py:53
  C:\Users\Admin\AppData\Roaming\Python\Python312\site-packages\starlette\testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

tests/unit/test_ac06_ac08_ac09_integration.py::test_ac06_discharge_bill_exceeds_buffer_rejected
  C:\Users\Admin\AppData\Roaming\Python\Python312\site-packages\fastapi\telemetry\_api.py:240: StarletteDeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated. Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.
    return function(**arguments)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
99 passed, 2 warnings in 10.07s
```

### Full Repository Test Suite (Including E2E)
**Command**:
```powershell
python -m pytest tests -q
```

**Actual Execution Output**:
```
........................................................................ [ 72%]
............................                                             [100%]
100 passed, 2 warnings in 23.24s
```

### Baseline Summary Metrics:
- **Total Tests**: 100 (99 Unit / Architecture / Security + 1 Playwright E2E)
- **Failures**: 0
- **Errors**: 0
- **Warnings**: 2 (Starlette / AnyIO deprecation notices from third-party packages)
- **Execution Time**: ~10.07s (unit/arch/sec), ~23.24s (full suite with Playwright)

---

## 3. Baseline Code Coverage Audit

**Command**:
```powershell
python -m pytest --cov=src --cov-report=term-missing tests/unit tests/architecture tests/security
```

**Actual Coverage Output**:
```
Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
src\__init__.py                                    0      0   100%
src\controllers\__init__.py                        0      0   100%
src\controllers\auth_dependency.py                26      1    96%   26
src\controllers\claim_controller.py               57      7    88%   57, 60-61, 87-90
src\controllers\eligibility_controller.py         49      6    88%   75-79, 104
src\controllers\health_controller.py               6      0   100%
src\controllers\network_admin_controller.py       64      9    86%   73-74, 93-94, 137-141
src\controllers\pre_auth_controller.py            49      7    86%   54, 60-61, 84-87
src\controllers\reports_controller.py             29      0   100%
src\controllers\settlement_controller.py          35      9    74%   34-39, 47, 53-54
src\domain\__init__.py                             0      0   100%
src\domain\adjudication_rule.py                   42      4    90%   31, 33, 37, 63
src\domain\admission_rule.py                      36      4    89%   20, 22, 50, 52
src\domain\claim_state_rule.py                    26      2    92%   51-52
src\domain\eligibility_rule.py                    56      4    93%   28, 30, 40, 57
src\domain\network_admin_rule.py                  31     10    68%   34, 36, 38, 40, 42, 55, 57, 59, 63, 65
src\domain\network_hospital_rule.py                7      0   100%
src\domain\notification_rule.py                   29      0   100%
src\domain\pre_auth_rule.py                       85      5    94%   34, 52, 102, 156, 188
src\domain\reports_rule.py                        36      3    92%   38, 68, 81
src\domain\role_boundary_rule.py                  26      2    92%   39, 50
src\domain\settlement_rule.py                     48      2    96%   43, 45
src\main.py                                       45      3    93%   20-22
src\repositories\__init__.py                       0      0   100%
src\repositories\claim_repository.py              66      1    98%   74
src\repositories\database.py                      25      9    64%   35-44
src\repositories\hospital_repository.py           25     11    56%   15, 40-49, 52-60
src\repositories\models.py                       204      0   100%
src\repositories\network_admin_repository.py      68     16    76%   31-38, 47-52, 70, 132-137, 152-155
src\repositories\policy_repository.py             25      1    96%   35
src\repositories\pre_auth_repository.py           34      2    94%   88, 91
src\repositories\settlement_repository.py         18      1    94%   60
src\seed_data.py                                  83      6    93%   17, 326-329, 335
src\services\__init__.py                           0      0   100%
src\services\admission_service.py                 62      3    95%   46, 52, 108
src\services\eligibility_service.py               44      6    86%   80, 96-99, 112
src\services\network_admin_service.py             28      2    93%   67, 132
src\services\pre_auth_service.py                  70      7    90%   74-76, 172, 236, 261-262
src\services\reports_service.py                   92     15    84%   39, 44-45, 50-51, 62, 77-78, 83-84, 113-114, 119-120, 130
src\services\settlement_service.py                58      5    91%   47, 55, 169, 187-188
src\utils\__init__.py                              0      0   100%
src\utils\logger.py                               34      1    97%   43
----------------------------------------------------------------------------
TOTAL                                           1718    164    90%
```

- **Statements**: 1,718
- **Missed**: 164
- **Coverage**: **90%** (Exceeds 80% requirement)

---

## 4. Repository & Artifact Inspection

| Category | Component / Artifact | Status | Findings |
|---|---|---|---|
| **Root Documents** | `README.md`, `CLAUDE.md`, `AGENTS.md` | Verified | Detailed startup instructions, invariants, and navigation table. |
| **Specifications** | `specs/app_spec.md` + 7 domain specs | Complete | All 8 specs present and aligned with architecture and AC-01..10. |
| **Documentation** | `docs/architecture.md`, `docs/tdd.md`, `docs/business-case.md` | Complete | Layered architecture, red-green-refactor example, business value. |
| **AI Substrate** | `.claude/` (14 agents, 7 skills, 5 commands, 4 hooks) | Complete | Full substrate matching `plugin.json`. |
| **MCP** | `.mcp.json` | Configured | `@executeautomation/playwright-mcp-server` configured. |
| **Plugin** | `plugin.json` | Valid | Substrate manifest valid JSON and references existing files. |
| **CI/CD** | `.gitlab-ci.yml` | 10 Stages | Stages: install, lint, migrate, test, architecture, security, coverage, playwright, evaluate, build. |
| **Sprint Contracts** | `sprint-contracts/` (15 contracts: Sprints 0–14) | Present | Full contract chain documented. |
| **Evaluator Reviews** | `specs/reviews/` (15 review reports + dispatches) | Present | Evaluator assessments for all sprints. |
| **E2E Visuals** | `tests/e2e/snapshots/` (14 PNG screenshots) | Valid | Freshly regenerated by real Playwright execution. |
| **Startup Runner** | `scripts/start.py` | Operational | Validates runtime, runs migrations, seeds synthetic data, boots server. |
| **LOC Audit** | `scripts/loc_report.py` | 6,976 LOC | Far exceeds >= 3,000 meaningful LOC mandate. |

---

## 5. Identified Blockers & Gaps to Close

1. **Dependency Management (BLOCKER)**:
   - No `requirements.txt` or `pyproject.toml` exists in the repository.
   - Clean environment installations cannot be reproduced without a declared dependency manifest.
   - **Resolution**: Create comprehensive `requirements.txt` and `pyproject.toml` capturing all required runtime, test, security, coverage, playwright, and SDK packages with exact proven versions.

2. **Git Remote Origin Status**:
   - `git remote -v` is empty. No remote GitLab instance is configured in the environment.
   - Merges are preserved locally as 17 `--no-ff` merge commits across feature branches to main.
   - **Resolution**: Truthfully document remote PR push requirement as `BLOCKED (User Action Required)` while detailing full local PR-driven Git history and providing instructions.

3. **Claude Agent SDK Execution Status**:
   - SDK `anthropic` v1.11.0 is installed and importable.
   - `--verify-sdk` succeeds.
   - Mocked test suite passes.
   - Live execution (`--execute`) requires `ANTHROPIC_API_KEY` which is not present in the local environment.
   - **Resolution**: Truthfully report live execution as `BLOCKED (No API Key)` while reporting programmatic SDK runner, tool schema, CLI options, and mocked execution as `PASS`.

4. **Structured Evidence Documents**:
   - The capstone requires dedicated evidence files under `docs/final-verification/`:
     - `acceptance-criteria.md`
     - `non-functional-requirements.md`
     - `agent-sdk.md`
     - `playwright.md`
     - `harness.md`
     - `coverage.md`
     - `ci.md`
     - `requirements-traceability.md`
   - **Resolution**: Generate thorough, genuine, command-backed evidence files for each requirement category.
