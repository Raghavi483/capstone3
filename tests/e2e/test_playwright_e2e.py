"""
End-to-End Browser Test Suite using Playwright (Section 13)
Executes real automated browser workflows against the MediCard single page application:
1. Customer Registration (AC-01)
2. Policy Coverage Inspection (AC-01)
3. Hospital Eligibility Lookup (AC-02)
4. Pre-Auth Submission (AC-03, AC-05)
5. Pre-Auth Decision Inspection (AC-04)
6. Case Status Timeline Inspection (AC-09)
7. Settlement Breakdown Inspection (AC-07)
8. Insurer Admin Override (AC-10)
9. Security Role Boundary Check (Section 8)
Captures browser snapshots into tests/e2e/snapshots/
"""

import os
from pathlib import Path
import threading
import time
import pytest
import uvicorn
from playwright.sync_api import sync_playwright
from src.main import app
from src.repositories.database import init_db
from src.seed_data import seed_database

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8555
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app, host=SERVER_HOST, port=SERVER_PORT, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


@pytest.fixture(scope="module", autouse=True)
def live_server():
    """Starts local FastAPI test server on port 8555 for Playwright."""
    init_db()
    seed_database()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    server = ServerThread()
    server.start()
    time.sleep(1.5)
    yield
    server.stop()


def test_playwright_e2e_full_lifecycle():
    """
    Executes full multi-party browser validation across Customer, Hospital,
    and Insurer Admin portals with Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Handle dialogs automatically
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Navigate to Application
        page.goto(BASE_URL)
        page.wait_for_selector(".navbar")
        assert "MediCard" in page.title()
        page.screenshot(path=str(SNAPSHOT_DIR / "01_homepage.png"))

        # 2. Customer Registration Flow (AC-01)
        page.fill("#reg-member-id", "MEM-PW-01")
        page.fill("#reg-name", "Playwright Test User")
        page.fill("#reg-email", "pw.user@example.com")
        page.fill("#reg-policy-id", "POL-PW-01")
        page.fill("#reg-sum-insured", "600000.00")
        with page.expect_response("**/api/v1/customers/register"):
            page.click("#btn-customer-register")
        page.wait_for_selector("#coverage-card", state="visible")
        page.screenshot(path=str(SNAPSHOT_DIR / "02_customer_registered.png"))

        # 3. Policy Coverage Fetch (AC-01)
        page.fill("#lookup-member-id", "MEM-1001")
        page.fill("#lookup-policy-id", "POL-5001")
        with page.expect_response("**/api/v1/customers/MEM-1001/policies/POL-5001/coverage"):
            page.click("#btn-fetch-coverage")
        cov_text = page.inner_text("#cov-sum-insured")
        assert "500,000" in cov_text or "5,00,000" in cov_text
        page.screenshot(path=str(SNAPSHOT_DIR / "03_coverage_dashboard.png"))

        # 4. Hospital Eligibility Lookup (AC-02)
        page.click("#tab-btn-hospital")
        page.wait_for_selector("#portal-hospital", state="visible")
        page.fill("#check-member-id", "MEM-1001")
        page.fill("#check-policy-id", "POL-5001")
        page.fill("#check-hospital-id", "HOSP-001")
        with page.expect_response("**/api/v1/eligibility/check"):
            page.click("#btn-check-eligibility")
        page.wait_for_selector("#eligibility-result-banner", state="visible")
        assert "ELIGIBLE" in page.inner_text("#elig-status-text")
        page.screenshot(path=str(SNAPSHOT_DIR / "04_eligibility_lookup.png"))

        # 5. Pre-Auth Submission & Decision (AC-03, AC-04, AC-05)
        page.fill("#pa-member-id", "MEM-1001")
        page.fill("#pa-policy-id", "POL-5001")
        page.fill("#pa-hospital-id", "HOSP-001")
        page.fill("#pa-diagnosis", "ACUTE_APPENDICITIS")
        page.fill("#pa-estimated-cost", "45000.00")
        page.fill("#pa-admission-date", "2026-11-20")
        with page.expect_response("**/api/v1/preauth/submit"):
            page.click("#btn-submit-preauth")
        page.wait_for_selector("#preauth-decision-banner", state="visible")
        assert "APPROVED" in page.inner_text("#pa-decision-status")
        page.screenshot(path=str(SNAPSHOT_DIR / "05_preauth_approved.png"))

        # 6. Patient Admission (AC-06, AC-08)
        page.fill("#admit-date", "2026-11-20")
        with page.expect_response("**/api/v1/claims/*/admit"):
            page.click("#btn-admit-patient")
        page.wait_for_selector("#admit-feedback", state="visible")
        page.screenshot(path=str(SNAPSHOT_DIR / "06_patient_admitted.png"))

        # 7. Final Bill & Discharge within Buffer (AC-06)
        page.fill("#dis-date", "2026-11-23")
        page.fill("#dis-final-bill", "48000.00")
        page.fill("#dis-proc-code", "PR-APP-01")
        page.fill("#dis-proc-desc", "Appendectomy")
        page.fill("#dis-proc-cost", "48000.00")
        with page.expect_response("**/api/v1/claims/*/discharge"):
            page.click("#btn-discharge-patient")
        page.wait_for_selector("#discharge-feedback", state="visible")
        page.screenshot(path=str(SNAPSHOT_DIR / "07_patient_discharged.png"))

        # 8. Insurer Workbench & Admin Override (AC-10)
        page.click("#tab-btn-insurer")
        page.wait_for_selector("#portal-insurer", state="visible")
        page.fill("#ov-preauth-id", "PA-2002")
        page.select_option("#ov-decision", "APPROVED")
        page.fill("#ov-amount", "50000.00")
        page.fill("#ov-reason", "Exceptional clinical reconstructive necessity approved by CMO")
        page.select_option("#ov-role-header", "ADMIN")
        with page.expect_response("**/api/v1/admin/preauth/override"):
            page.click("#btn-execute-override")
        page.wait_for_selector("#override-result-banner", state="visible")
        assert "Override Success" in page.inner_text("#override-result-banner")
        page.screenshot(path=str(SNAPSHOT_DIR / "08_admin_override.png"))

        # 9. Role Boundary Test in UI (Section 8)
        page.select_option("#ov-role-header", "HOSPITAL")  # Unauthorized
        with page.expect_response("**/api/v1/admin/preauth/override"):
            page.click("#btn-execute-override")
        page.wait_for_selector("#override-result-banner.error", state="visible")
        assert "Override Rejected (403)" in page.inner_text("#override-result-banner")
        page.screenshot(path=str(SNAPSHOT_DIR / "09_role_boundary_blocked.png"))

        # 10. Settlement Calculation (AC-07)
        page.fill("#calc-claim-id", "CLM-3001")
        page.fill("#calc-deductible", "1000.00")
        page.fill("#calc-copay", "2000.00")
        with page.expect_response("**/api/v1/claims/*/settle"):
            page.click("#btn-finalize-settlement")
        page.wait_for_selector("#calc-settlement-feedback", state="visible")
        page.screenshot(path=str(SNAPSHOT_DIR / "10_settlement_finalized.png"))

        # 11. Customer Timeline & Settlement Verification (AC-07, AC-09)
        page.click("#tab-btn-customer")
        page.wait_for_selector("#portal-customer", state="visible")
        page.fill("#timeline-claim-id", "CLM-3001")
        with page.expect_response("**/api/v1/claims/*/timeline"):
            page.click("#btn-fetch-timeline")
        page.screenshot(path=str(SNAPSHOT_DIR / "11_customer_timeline.png"))

        page.fill("#settlement-claim-id", "CLM-3001")
        with page.expect_response("**/api/v1/claims/*/settlement"):
            page.click("#btn-fetch-settlement")
        page.wait_for_selector("#settlement-details-card", state="visible")
        settle_text = page.inner_text("#set-insurer-payout")
        assert "45,000" in settle_text or "45000" in settle_text
        page.screenshot(path=str(SNAPSHOT_DIR / "12_customer_settlement_breakdown.png"))

        # 12. Reports & Analytics View (Priority 2, AC-REP-01..03)
        page.click("#tab-btn-reports")
        page.wait_for_selector("#portal-reports", state="visible")
        with page.expect_response("**/api/v1/reports/analytics"):
            page.click("#btn-refresh-analytics")
        page.wait_for_selector("#rep-mean-tat", state="visible")
        page.screenshot(path=str(SNAPSHOT_DIR / "13_reports_analytics.png"))

        # 13. Network & Coverage Administration (Priority 1, AC-NET-01..03)
        page.click("#tab-btn-admin")
        page.wait_for_selector("#portal-admin", state="visible")
        page.fill("#onboard-hospital-id", "HOSP-PW-99")
        page.fill("#onboard-hospital-name", "Playwright Metro Care")
        page.fill("#onboard-city", "Hyderabad")
        page.fill("#onboard-state", "Telangana")
        page.select_option("#onboard-tier", "TIER_1")
        with page.expect_response("**/api/v1/admin/hospitals/onboard"):
            page.click("#btn-onboard-hospital")
        page.wait_for_selector("#onboard-feedback", state="visible")
        assert "successfully onboarded" in page.inner_text("#onboard-feedback")
        page.screenshot(path=str(SNAPSHOT_DIR / "14_network_admin_onboarding.png"))

        browser.close()
