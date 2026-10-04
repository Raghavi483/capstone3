# Sprint 7 Contract — Local Startup, Meaningful LOC, CI/CD Pipeline & Final Compliance (Sections 17, 18, 19, 25)
**Sprint**: Sprint 7  
**Target Acceptance Criteria**: Sections 17 (CI/CD), 18 (One-command Startup), 19 (3,000+ Meaningful LOC), 25 (Final Compliance Report)  
**Associated Specifications**: `specs/app_spec.md`, `CLAUDE.md`, `AGENTS.md`  
**Primary Agent**: `planner.md`, `test-engineer.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-7-startup-and-ci`  

---

## 1. Scope & Deliverables
1. **One-Command Local Startup Script (`scripts/start.py`)**:
   - Environment and prerequisite validation (Python 3.12+, SQLite).
   - Automated database initialization via `init_db()`.
   - Automated deterministic synthetic seed data insertion via `seed_database()`.
   - Starts FastAPI backend via `uvicorn src.main:app --host 127.0.0.1 --port 8000`.
   - Automatically serves frontend SPA on `http://127.0.0.1:8000/`.
   - Health latency validation probe before opening browser.
2. **Executable CI/CD Pipeline (`.gitlab-ci.yml`)**:
   - Stages: `install`, `lint`, `test`, `architecture`, `security`, `coverage`.
   - Execution against real Python environment and test suites.
   - Generation of real `coverage.xml` artifact.
3. **LOC Audit & Report Tool (`scripts/loc_report.py`)**:
   - Non-blank, non-comment lines of code across:
     - Backend (domain, services, repositories, controllers, utils).
     - Frontend (HTML, CSS, JS).
     - Tests (unit, architecture, security, E2E).
   - Validation against the $\ge 3,000$ meaningful LOC capstone target.
4. **Comprehensive Documentation & Quickstart (`README.md`)**:
   - One-command quickstart guide.
   - Prerequisites, installation, environment variables.
   - Test execution commands, Playwright E2E execution, coverage generation.
   - Demo persona accounts and roles.
   - API endpoints catalog.
5. **Final Compliance Report (`docs/final-compliance-report.md`)**:
   - Exhaustive compliance matrix across AC-01 through AC-10, NFR-01 through NFR-08, database, frontend, Playwright, coverage, CI, LOC, PR history, and Claude Code agent dispatches.
