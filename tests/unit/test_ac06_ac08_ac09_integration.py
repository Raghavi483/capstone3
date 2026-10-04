"""
Test Suite: AC-06, AC-08, AC-09 Integration Tests
Verifies admission recording, procedure updates, buffer cap validation,
strict claim state transitions, timeline generation, and notifications.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.database import SessionLocal, init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_ac06_and_ac08_admission_and_discharge_happy_path():
    """AC-06 & AC-08: Complete flow from pre-auth approval to admission and discharge within buffer."""
    # 1. Submit pre-auth (auto-approved up to 45,000)
    pa_res = client.post("/api/v1/preauth/submit", json={
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "ACUTE_APPENDICITIS",
        "estimated_cost": "45000.00",
        "expected_admission_date": "2026-11-01"
    })
    assert pa_res.status_code == 201
    claim_id = pa_res.json()["claim_id"]

    # 2. Admit patient (AC-08: PRE_AUTH -> ADMITTED)
    admit_res = client.post(f"/api/v1/claims/{claim_id}/admit", json={
        "admission_date": "2026-11-01",
        "hospital_id": "HOSP-001"
    })
    assert admit_res.status_code == 200
    assert admit_res.json()["status"] == "ADMITTED"

    # 3. Discharge with final bill within 10% buffer (45k + 4.5k = 49.5k cap; bill = 48k)
    discharge_res = client.post(f"/api/v1/claims/{claim_id}/discharge", json={
        "discharge_date": "2026-11-04",
        "final_bill": "48000.00",
        "hospital_id": "HOSP-001",
        "procedures": [
            {"procedure_code": "PR-APP-01", "description": "Appendectomy", "cost": "40000.00"},
            {"procedure_code": "PR-MED-01", "description": "Post-op Care", "cost": "8000.00"}
        ]
    })
    assert discharge_res.status_code == 200
    d_data = discharge_res.json()
    assert d_data["status"] == "DISCHARGED"
    assert d_data["effective_bill"] == "48000.00"
    assert d_data["bill_cap"] == "49500.00"

    # 4. Verify Timeline (AC-09)
    timeline_res = client.get(f"/api/v1/claims/{claim_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    types = [e["event_type"] for e in events]
    assert "ADMITTED" in types
    assert "DISCHARGED" in types

    # 5. Verify Notifications (AC-09)
    notif_res = client.get("/api/v1/notifications/MEM-1001")
    assert notif_res.status_code == 200
    assert len(notif_res.json()) >= 1


def test_ac06_discharge_bill_exceeds_buffer_rejected():
    """AC-06 Scenario 2: Hospital bill exceeding pre-auth + 10% buffer is rejected (HTTP 422)."""
    # 1. Pre-auth 50,000 (auto-approved)
    pa_res = client.post("/api/v1/preauth/submit", json={
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "CATARACT_SURGERY",
        "estimated_cost": "50000.00",
        "expected_admission_date": "2026-11-10"
    })
    claim_id = pa_res.json()["claim_id"]

    # 2. Admit
    client.post(f"/api/v1/claims/{claim_id}/admit", json={
        "admission_date": "2026-11-10",
        "hospital_id": "HOSP-001"
    })

    # 3. Submit final bill of 62,000 (exceeds 55,000 buffer cap)
    discharge_res = client.post(f"/api/v1/claims/{claim_id}/discharge", json={
        "discharge_date": "2026-11-11",
        "final_bill": "62000.00",
        "hospital_id": "HOSP-001",
        "procedures": [
            {"procedure_code": "PR-CAT-01", "description": "Cataract Surgery", "cost": "62000.00"}
        ]
    })
    assert discharge_res.status_code == 422
    assert "BILL_EXCEEDS_BUFFER_CAP" in discharge_res.json()["detail"]


def test_ac08_invalid_claim_state_transition_fails():
    """AC-08: Attempting to admit a claim already discharged or skipping states raises HTTP 409."""
    # Attempting to discharge a non-admitted claim
    pa_res = client.post("/api/v1/preauth/submit", json={
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "NORMAL_DELIVERY",
        "estimated_cost": "40000.00",
        "expected_admission_date": "2026-11-15"
    })
    claim_id = pa_res.json()["claim_id"]

    # Directly discharge without admit -> InvalidClaimStateException (HTTP 409)
    res = client.post(f"/api/v1/claims/{claim_id}/discharge", json={
        "discharge_date": "2026-11-16",
        "final_bill": "40000.00",
        "hospital_id": "HOSP-001",
        "procedures": []
    })
    assert res.status_code == 409
    assert "Cannot transition claim from PRE_AUTH to DISCHARGED" in res.json()["detail"]
