"""
Test Suite: AC-03, AC-04, AC-05, AC-10 Integration Tests
Verifies Pre-Auth submission, auto-approval engine, decision ledgers,
and elevated admin overrides via REST API.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.database import SessionLocal, init_db
from src.repositories.models import AuditEventModel, PreAuthDecisionModel

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_ac03_and_ac05_pre_auth_submission_auto_approval():
    """AC-03 & AC-05: Submitting valid appendicitis case under 50k auto-approves."""
    payload = {
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "ACUTE_APPENDICITIS",
        "estimated_cost": "45000.00",
        "expected_admission_date": "2026-10-20"
    }
    response = client.post("/api/v1/preauth/submit", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "APPROVED"
    assert data["estimated_cost"] == "45000.00"
    assert data["approved_amount"] == "45000.00"
    assert "AUTO_APPROVED_RULE_01" in data["reason_codes"]
    assert data["pre_auth_id"].startswith("PA-")
    assert data["claim_id"].startswith("CLM-")


def test_ac05_pre_auth_auto_rejection_excluded_diagnosis():
    """AC-05: Submitting excluded condition auto-rejects."""
    payload = {
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "COSMETIC_SURGERY",
        "estimated_cost": "30000.00",
        "expected_admission_date": "2026-10-22"
    }
    response = client.post("/api/v1/preauth/submit", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "REJECTED"
    assert data["approved_amount"] == "0.00"
    assert "EXCLUDED_CONDITION" in data["reason_codes"]


def test_ac10_admin_override_and_audit():
    """AC-10: Admin role successfully overrides rejected pre-auth with audit trail."""
    # 1. Create a rejected pre-auth
    sub_payload = {
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "COSMETIC_SURGERY",
        "estimated_cost": "50000.00",
        "expected_admission_date": "2026-10-25"
    }
    sub_res = client.post("/api/v1/preauth/submit", json=sub_payload)
    pa_id = sub_res.json()["pre_auth_id"]

    # 2. Execute Admin Override
    override_payload = {
        "pre_auth_id": pa_id,
        "override_decision": "APPROVED",
        "override_amount": "50000.00",
        "reason": "Exceptional clinical reconstructive necessity approved by CMO",
        "actor_id": "admin_cmo_01"
    }
    override_res = client.post(
        "/api/v1/admin/preauth/override",
        json=override_payload,
        headers={"X-User-Role": "ADMIN"}
    )
    assert override_res.status_code == 200
    ov_data = override_res.json()
    assert ov_data["status"] == "APPROVED"
    assert ov_data["approved_amount"] == "50000.00"
    assert ov_data["is_override"] is True

    # 3. Verify audit record
    db = SessionLocal()
    try:
        audit = db.query(AuditEventModel).filter(
            AuditEventModel.entity_type == "PRE_AUTH_OVERRIDE",
            AuditEventModel.entity_id == pa_id
        ).first()
        assert audit is not None
        assert audit.actor_role == "ADMIN"
        assert audit.actor_id == "admin_cmo_01"
    finally:
        db.close()


def test_ac10_non_admin_override_forbidden():
    """AC-10: Hospital or Customer attempting override is blocked with HTTP 403."""
    override_payload = {
        "pre_auth_id": "PA-2002",
        "override_decision": "APPROVED",
        "override_amount": "50000.00",
        "reason": "Attempting unauthorized override",
        "actor_id": "hosp_user_01"
    }
    response = client.post(
        "/api/v1/admin/preauth/override",
        json=override_payload,
        headers={"X-User-Role": "HOSPITAL"}  # Unauthorized role
    )
    assert response.status_code == 403
    assert "Only ADMIN role can execute overrides" in response.json()["detail"]


def test_ac04_pre_auth_details_and_decision_history():
    """AC-04: Confirms pre-auth decision ledger preserves history."""
    sub_payload = {
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "ACUTE_APPENDICITIS",
        "estimated_cost": "40000.00",
        "expected_admission_date": "2026-10-30"
    }
    sub_res = client.post("/api/v1/preauth/submit", json=sub_payload)
    pa_id = sub_res.json()["pre_auth_id"]

    res = client.get(f"/api/v1/preauth/{pa_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["pre_auth_id"] == pa_id
    assert len(data["decisions"]) >= 1
    assert data["decisions"][0]["decision"] == "APPROVED"
