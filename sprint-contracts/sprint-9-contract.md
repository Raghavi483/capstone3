# Sprint 9 Contract — Operational Reports & Analytics (Priority 2)
**Sprint**: Sprint 9  
**Target Acceptance Criteria**: AC-REP-01, AC-REP-02, AC-REP-03, REP-01, REP-02, Section 5  
**Associated Specifications**: `specs/reports_spec.md`, `specs/app_spec.md`  
**Primary Agent**: `planner.md`, `test-engineer.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-9-reports-analytics`  

---

## 1. Scope & Deliverables
1. **Analytics Domain Engine (`src/domain/reports_rule.py`)**:
   - Computation of pre-authorization turnaround time (mean, median, 95th percentile in seconds).
   - Query frequency rate by hospital facility (`{hospital_id: query_percentage}`).
   - Settlement volumes (total settled claim count, total payout amount formatted strictly as Decimal).
   - Loss ratio calculation: `total_settled_payout / total_earned_premium` (quantized Decimal).
   - Top diagnoses frequency distribution table.
   - Privacy Rule REP-01: Zero patient names or member IDs in aggregate reports.
   - Monetary Rule REP-02: Zero floating-point arithmetic.
2. **Analytics Service (`src/services/reports_service.py`)**:
   - Queries `pre_authorizations`, `pre_auth_decisions`, `settlements`, `policies` across optional date range and hospital filters.
   - Aggregates operational metrics deterministically from real database records.
3. **Analytics API Controller (`src/controllers/reports_controller.py`)**:
   - `GET /api/v1/reports/analytics` — Comprehensive operational BI analytics DTO.
   - `GET /api/v1/reports/turnaround-time` — TAT metrics across network hospitals.
   - `GET /api/v1/reports/query-rates` — Query rate percentages by hospital.
   - `GET /api/v1/reports/settlement-summary` — Total settled volume and loss ratio.
   - Security: Role `INSURER` or `ADMIN` required; other roles receive 403 Forbidden.
4. **Unit & Acceptance Tests (`tests/unit/test_ac_rep_reports.py`)**:
   - Explicit tests referencing `AC-REP-01`, `AC-REP-02`, `AC-REP-03`.
   - Tests for TAT statistics, query rate calculations, loss ratio Decimal precision, empty dataset handling, and role boundary rejection.
5. **Frontend Integration (`frontend/app.js`, `frontend/index.html`)**:
   - Update Reports & Analytics portal to consume real `/api/v1/reports/analytics` data.
