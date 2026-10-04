"""
Acceptance Criteria Tests: Network Hospital & Coverage Administration (specs/network_admin_spec.md).
Explicitly tests:
- AC-NET-01: Admin can onboard a new network hospital and toggle active status.
- AC-NET-02: Admin can configure auto-approval thresholds and diagnostic whitelists for a policy product.
- AC-NET-03: Network hospital directory is queryable by city and tier.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.database import SessionLocal, init_db
from src.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    seed_database()
    yield


def test_ac_net_01_admin_onboard_hospital():
    """AC-NET-01: Admin can onboard a new network hospital and record its tier."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    payload = {
        "hospital_id": "HOSP-002",
        "name": "St. Jude Memorial Hospital",
        "tier": "TIER_1",
        "city": "Metropolis",
        "state": "NY",
        "is_active": True
    }
    response = client.post("/api/v1/admin/hospitals/onboard", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["hospital_id"] == "HOSP-002"
    assert data["name"] == "St. Jude Memorial Hospital"
    assert data["tier"] == "TIER_1"
    assert data["is_active"] is True


def test_ac_net_01_admin_toggle_active_status():
    """AC-NET-01: Admin can toggle hospital active status (suspend / reactivate)."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    
    # Toggle active status to False
    res_deactivate = client.patch(
        "/api/v1/admin/hospitals/HOSP-001/status",
        json={"is_active": False},
        headers=headers
    )
    assert res_deactivate.status_code == 200
    assert res_deactivate.json()["is_active"] is False

    # Check eligibility reflects deactivated status
    elig_res = client.post(
        "/api/v1/eligibility/check",
        json={"member_id": "MEM-1001", "policy_id": "POL-5001", "hospital_id": "HOSP-001"},
        headers={"X-User-Role": "HOSPITAL", "X-Hospital-Id": "HOSP-001"}
    )
    assert elig_res.status_code == 200
    assert elig_res.json()["status"] == "NOT_ELIGIBLE"
    assert "HOSP_OUT_OF_NETWORK" in elig_res.json()["reason_codes"]

    # Reactivate
    res_reactivate = client.patch(
        "/api/v1/admin/hospitals/HOSP-001/status",
        json={"is_active": True},
        headers=headers
    )
    assert res_reactivate.status_code == 200
    assert res_reactivate.json()["is_active"] is True


def test_ac_net_01_non_admin_cannot_onboard_hospital():
    """AC-NET-01: Non-admin actors cannot onboard network hospitals."""
    # Attempt as HOSPITAL role
    headers = {"X-User-Role": "HOSPITAL", "X-Hospital-Id": "HOSP-001"}
    payload = {
        "hospital_id": "HOSP-UNAUTH",
        "name": "Rogue Hospital",
        "tier": "TIER_3",
        "city": "Gotham",
        "state": "NJ",
        "is_active": True
    }
    response = client.post("/api/v1/admin/hospitals/onboard", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Admin role required" in response.json()["detail"]


def test_ac_net_02_admin_configure_policy_thresholds():
    """AC-NET-02: Admin can configure auto-approval thresholds and diagnostic whitelists."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    payload = {
        "policy_code": "POL-SILVER-001",
        "product_name": "Silver Health Guard",
        "default_sum_insured": "300000.00",
        "auto_approval_threshold": "35000.00",
        "buffer_percentage": "0.10",
        "auto_approved_diagnoses": ["Acute Appendicitis", "Fracture Reduction", "Cataract Surgery"],
        "exclusions": ["Cosmetic Surgery", "Pre-existing Condition Year 1"]
    }
    response = client.post("/api/v1/admin/policies/configure", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["policy_code"] == "POL-SILVER-001"
    assert Decimal(str(data["auto_approval_threshold"])) == Decimal("35000.00")
    assert "Cataract Surgery" in data["auto_approved_diagnoses"]


def test_ac_net_02_negative_threshold_rejected():
    """AC-NET-02: Negative auto-approval threshold is rejected with 400 Bad Request."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    payload = {
        "policy_code": "POL-INVALID",
        "product_name": "Invalid Policy",
        "default_sum_insured": "100000.00",
        "auto_approval_threshold": "-500.00",
        "buffer_percentage": "0.10",
        "auto_approved_diagnoses": ["Appendicitis"],
        "exclusions": []
    }
    response = client.post("/api/v1/admin/policies/configure", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Threshold must be non-negative" in response.json()["detail"]


def test_ac_net_03_query_directory_by_city_and_tier():
    """AC-NET-03: Network hospital directory is queryable by city and tier."""
    headers = {"X-User-Role": "ADMIN"}
    
    # Query all
    res_all = client.get("/api/v1/admin/hospitals", headers=headers)
    assert res_all.status_code == 200
    hospitals = res_all.json()
    assert len(hospitals) >= 1

    # Query with city filter
    res_city = client.get("/api/v1/admin/hospitals?city=New+York", headers=headers)
    assert res_city.status_code == 200
    assert all("New York" in h["city"] for h in res_city.json())

    # Query with tier filter
    res_tier = client.get("/api/v1/admin/hospitals?tier=TIER_1", headers=headers)
    assert res_tier.status_code == 200
    assert all(h["tier"] == "TIER_1" for h in res_tier.json())
