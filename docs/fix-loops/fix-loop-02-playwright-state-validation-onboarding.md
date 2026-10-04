# Fix-Loop 02: Playwright Hospital Onboarding State Validation & Endpoint Prefix
**Component**: `frontend/app.js`, `frontend/index.html`, `tests/e2e/test_playwright_e2e.py`  
**Date**: 2026-10-04  
**Trigger**: Playwright E2E Test Suite (`test_playwright_e2e_full_lifecycle`)  
**Status**: **RESOLVED**  

---

## 1. Symptom
During execution of `python -m pytest tests/e2e/test_playwright_e2e.py -v -s` on the newly integrated Network Administration step, the assertion failed:
```
AssertionError: assert 'successfully onboarded' in 'Onboarding failed: state cannot be empty'
```
Previously, the endpoint had also returned `404 Not Found` because frontend invoked `/admin/hospitals/onboard` rather than `/api/v1/admin/hospitals/onboard`.

---

## 2. Environment Check
- Browser Test Engine: Playwright Chromium (sync API)
- Backend: FastAPI with `APIRouter(prefix="/api/v1/admin")`
- Domain Invariant: Rule NET-01 strictly validates hospital onboarding payload, requiring non-empty `state` attribute.

---

## 3. Root Cause Analysis
1. `NetworkAdminController` registers endpoints under prefix `/api/v1/admin`. The frontend `app.js` was invoking `/admin/hospitals/onboard` without the `API_BASE` (`/api/v1`) prefix.
2. In `frontend/index.html`, the hospital onboarding form included `Hospital ID`, `Network Tier`, `Facility Name`, and `City`, but omitted the `State` input. `validate_hospital_payload` in `src/domain/network_admin_rule.py` enforces `if not payload.state.strip(): raise InvalidHospitalPayloadException("state cannot be empty")`.

---

## 4. Remediation
1. Updated `frontend/app.js` to prefix all administration calls with `${API_BASE}/admin/...`.
2. Added `<input type="text" id="onboard-state" required value="Karnataka">` to the onboarding form in `frontend/index.html`.
3. Updated `frontend/app.js` `handleOnboardHospital` to extract `state` from `#onboard-state`.
4. Updated `tests/e2e/test_playwright_e2e.py` to fill `#onboard-state` with `"Telangana"`.

---

## 5. Validation & Evidence
Executed `python -m pytest tests/e2e/test_playwright_e2e.py -v -s`:
- Playwright E2E suite executed live and passed in 12.40s.
- 14 browser snapshots captured into `tests/e2e/snapshots/`, including `13_reports_analytics.png` and `14_network_admin_onboarding.png`.
