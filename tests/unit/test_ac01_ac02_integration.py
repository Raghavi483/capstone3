"""
Test Suite: AC-01 & AC-02 API & Service Integration Tests
Verifies end-to-end integration across Controller, Service, Domain, and Repository layers.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.database import SessionLocal, init_db
from src.repositories.models import AuditEventModel

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_ac01_customer_registration_api():
    """AC-01: Verifies customer registration and policy coverage response via API."""
    payload = {
        "member_id": "MEM-TEST-01",
        "name": "Integration User",
        "email": "user@example.com",
        "phone": "+1-555-0999",
        "policy_id": "POL-TEST-01",
        "product_name": "MediCard Platinum",
        "sum_insured": "750000.00",
        "exclusions": ["DENTAL", "COSMETIC"]
    }
    response = client.post("/api/v1/customers/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer"]["member_id"] == "MEM-TEST-01"
    assert data["coverage"]["policy_id"] == "POL-TEST-01"
    assert data["coverage"]["sum_insured"] == "750000.00"
    assert "DENTAL" in data["coverage"]["exclusions"]


def test_ac01_get_coverage_api():
    """AC-01: Verifies retrieval of customer policy coverage via API."""
    response = client.get("/api/v1/customers/MEM-1001/policies/POL-5001/coverage")
    assert response.status_code == 200
    data = response.json()
    assert data["member_id"] == "MEM-1001"
    assert data["policy_id"] == "POL-5001"
    assert Decimal(data["sum_insured"]) == Decimal("500000.00")
    assert "COSMETIC_SURGERY" in data["exclusions"]


def test_ac02_eligibility_check_api_eligible():
    """AC-02: Verifies eligible response for in-network hospital query via API."""
    payload = {
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001"
    }
    response = client.post("/api/v1/eligibility/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ELIGIBLE"
    assert data["is_eligible"] is True
    assert data["reason_codes"] == []


def test_ac02_eligibility_check_api_out_of_network_and_audit():
    """AC-02 & NFR-02: Verifies NOT_ELIGIBLE response for out-of-network hospital and audit logging."""
    payload = {
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-999"  # Out of network
    }
    response = client.post("/api/v1/eligibility/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NOT_ELIGIBLE"
    assert data["is_eligible"] is False
    assert "HOSP_OUT_OF_NETWORK" in data["reason_codes"]

    # Verify audit event was logged in database
    db = SessionLocal()
    try:
        audit = db.query(AuditEventModel).filter(
            AuditEventModel.entity_type == "ELIGIBILITY",
            AuditEventModel.actor_id == "HOSP-999"
        ).order_by(AuditEventModel.id.desc()).first()
        assert audit is not None
        assert audit.action == "ELIGIBILITY_LOOKUP"
        assert "HOSP_OUT_OF_NETWORK" in audit.changes_json
    finally:
        db.close()
