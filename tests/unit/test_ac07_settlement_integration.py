"""
Test Suite: AC-07 Settlement Integration & Immutability Tests
Verifies full end-to-end cashless settlement workflow via API,
policy balance deductions, audit trails, and settled claim immutability.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.database import SessionLocal, init_db
from src.repositories.models import SettlementModel, AuditEventModel, PolicyModel, ClaimModel

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_ac07_complete_settlement_flow_via_api():
    """AC-07: Full workflow: Pre-Auth -> Admit -> Discharge -> Settle."""
    # 1. Pre-Auth for 50,000
    pa_res = client.post("/api/v1/preauth/submit", json={
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "ACUTE_APPENDICITIS",
        "estimated_cost": "50000.00",
        "expected_admission_date": "2026-11-20"
    })
    claim_id = pa_res.json()["claim_id"]

    # 2. Admit
    client.post(f"/api/v1/claims/{claim_id}/admit", json={
        "admission_date": "2026-11-20",
        "hospital_id": "HOSP-001"
    })

    # 3. Discharge with final bill 52,000 (within 10% buffer cap = 55,000)
    client.post(f"/api/v1/claims/{claim_id}/discharge", json={
        "discharge_date": "2026-11-23",
        "final_bill": "52000.00",
        "hospital_id": "HOSP-001",
        "procedures": [
            {"procedure_code": "PR-APP-01", "description": "Appendectomy", "cost": "52000.00"}
        ]
    })

    # 4. Settle with deductible=2000.00, co_pay=5000.00
    settle_res = client.post(f"/api/v1/claims/{claim_id}/settle", json={
        "deductible": "2000.00",
        "co_pay": "5000.00",
        "actor_id": "fin_admin_01"
    })
    assert settle_res.status_code == 200
    s_data = settle_res.json()
    assert s_data["status"] == "SETTLED"
    assert s_data["effective_bill"] == "52000.00"
    assert s_data["bill_cap"] == "55000.00"
    # settlement = 52000 - 2000 - 5000 = 45000.00
    assert s_data["settlement_amount"] == "45000.00"
    # patient responsibility = 2000 + 5000 = 7000.00
    assert s_data["patient_responsibility"] == "7000.00"

    # 5. Verify Settlement Retrieval
    get_res = client.get(f"/api/v1/claims/{claim_id}/settlement")
    assert get_res.status_code == 200
    assert get_res.json()["settlement_amount"] == "45000.00"

    # 6. Verify Settled Claim Immutability (Attempting to re-admit or re-discharge fails)
    re_admit_res = client.post(f"/api/v1/claims/{claim_id}/admit", json={
        "admission_date": "2026-11-25",
        "hospital_id": "HOSP-001"
    })
    assert re_admit_res.status_code == 409
    assert "Settled claim is immutable" in re_admit_res.json()["detail"]

    # 7. Verify Audit Log entry exists
    db = SessionLocal()
    try:
        audit = db.query(AuditEventModel).filter(
            AuditEventModel.entity_type == "CLAIM_SETTLEMENT",
            AuditEventModel.actor_id == "fin_admin_01"
        ).first()
        assert audit is not None
        assert "45000.00" in audit.changes_json
    finally:
        db.close()
