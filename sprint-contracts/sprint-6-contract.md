# Sprint 6 Contract — Multi-Portal Frontend & Playwright Browser E2E Suite (Sections 12, 13)
**Sprint**: Sprint 6  
**Target Acceptance Criteria**: AC-01 through AC-10 (Full E2E Flows), Sections 12 & 13  
**Associated Specifications**: `specs/app_spec.md`, `specs/reports_spec.md`, `specs/network_admin_spec.md`  
**Primary Agent**: `ui-designer.md`, `design-critic.md`, `test-engineer.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-6-frontend-playwright`  

---

## 1. Scope & Deliverables
1. **Responsive Multi-Portal Frontend SPA (`frontend/index.html`, `frontend/index.css`, `frontend/app.js`)**:
   - Modern glassmorphic theme with dark mode, responsive grid, dynamic micro-animations, and Inter/Outfit typography.
   - Distinct role portals with switcher:
     - **Customer View**: Member registration, policy coverage lookup, active claims, case timeline, and detailed settlement breakdown.
     - **Hospital View**: Real-time eligibility lookup, cashless pre-authorization submission, patient admission/procedure logging, final bill submission, and claim tracking.
     - **Insurer / Admin Workbench**: Pre-auth review queue, adjudication decisions (approve, query, reject), admin override modal with mandatory justification, audit ledger view.
     - **Network Hospital Admin**: Registered network hospitals directory and tiering status.
     - **Reports & Analytics**: System-wide throughput, auto-approval rates, settlement ratios, and latency.
   - Live system health bar with active latency gauge communicating with `GET /health`.
2. **Playwright E2E Browser Test Suite (`tests/e2e/test_playwright_e2e.py`)**:
   - Real browser automation running headless Chromium via Playwright.
   - Comprehensive test flow verifying:
     - Homepage rendering and health check latency.
     - Customer registration and policy coverage display.
     - Hospital eligibility lookup for network member.
     - Pre-authorization auto-approval evaluation.
     - Patient admission, procedures, and final billing.
     - Admin override workflow for disputed/rejected cases.
     - Multi-tenant role boundary security verification (unauthorized access denial).
     - Settlement breakdown inspection and verification.
     - Complete case timeline rendering.
     - Reports and analytics summary rendering.
   - Capture of 13 visual snapshots into `tests/e2e/snapshots/`.

---

## 2. Invariants & Guardrails
- **No Mock UIs**: Real UI connected to FastAPI backend.
- **Deterministic Selectors**: All interactive elements equipped with explicit `data-testid` attributes.
- **PHI Masking**: Diagnosis and procedures masked in public views.
- **Visual Evidence**: Playwright snapshots captured and verified.
