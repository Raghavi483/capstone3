"""
Security Tests: Controller-Level Role & Authentication Boundaries (Priority 4, Section 8, NFR-04).
Verifies:
1. Unauthenticated requests to administrative endpoints return HTTP 401 Unauthorized.
2. Cross-customer coverage inspection returns HTTP 403 Forbidden.
3. Cross-hospital claim operations return HTTP 403 Forbidden.
4. Unauthorized role attempts (Customer/Hospital performing Admin actions) return HTTP 403 Forbidden.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    seed_database(force=True)
    yield


def test_unauthenticated_admin_override_returns_401():
    """Unauthenticated request to elevated override endpoint returns HTTP 401."""
    payload = {
        "pre_auth_id": "PA-2002",
        "override_decision": "APPROVED",
        "override_amount": "50000.00",
        "reason": "Missing auth headers test",
        "actor_id": "anonymous"
    }
    # Send request with zero authentication headers
    response = client.post("/api/v1/admin/preauth/override", json=payload)
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]


def test_customer_attempting_admin_override_returns_403():
    """Customer role attempting admin override is blocked with HTTP 403 Forbidden."""
    payload = {
        "pre_auth_id": "PA-2002",
        "override_decision": "APPROVED",
        "override_amount": "50000.00",
        "reason": "Customer attempting unauthorized override",
        "actor_id": "MEM-1001"
    }
    headers = {"X-User-Role": "CUSTOMER", "X-User-Id": "MEM-1001"}
    response = client.post("/api/v1/admin/preauth/override", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_hospital_attempting_network_onboarding_returns_403():
    """Hospital role attempting network administration onboarding is blocked with HTTP 403 Forbidden."""
    payload = {
        "hospital_id": "HOSP-ROGUE",
        "name": "Rogue Hospital",
        "tier": "TIER_1",
        "city": "Metropolis",
        "is_active": True
    }
    headers = {"X-User-Role": "HOSPITAL", "X-User-Id": "HOSP-001-USER", "X-Hospital-Id": "HOSP-001"}
    response = client.post("/api/v1/admin/hospitals/onboard", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_customer_accessing_other_customer_coverage_returns_403():
    """Customer authenticated as MEM-1001 attempting to inspect MEM-1002's coverage is blocked with 403."""
    headers = {
        "X-User-Role": "CUSTOMER",
        "X-User-Id": "MEM-1001",
        "X-Member-Id": "MEM-1001"
    }
    # Attempting to access MEM-1002
    response = client.get("/api/v1/customers/MEM-1002/coverage", headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_hospital_accessing_other_hospital_claim_returns_403():
    """Hospital A (HOSP-001) attempting to admit patient for Hospital B (HOSP-002) is blocked with 403."""
    headers = {
        "X-User-Role": "HOSPITAL",
        "X-User-Id": "hosp_user_1",
        "X-Hospital-Id": "HOSP-001"
    }
    payload = {
        "admission_date": "2026-11-20",
        "hospital_id": "HOSP-002"  # Mismatch with header HOSP-001
    }
    response = client.post("/api/v1/claims/CLM-1001/admit", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_authorized_admin_override_succeeds_200():
    """Authorized ADMIN role with valid authentication credentials successfully performs override."""
    # 1. Create rejected pre-auth
    sub_res = client.post("/api/v1/preauth/submit", json={
        "member_id": "MEM-1001",
        "policy_id": "POL-5001",
        "hospital_id": "HOSP-001",
        "diagnosis": "COSMETIC_SURGERY",
        "estimated_cost": "30000.00",
        "expected_admission_date": "2026-11-25"
    })
    pa_id = sub_res.json()["pre_auth_id"]

    # 2. Perform override with explicit ADMIN credentials
    headers = {
        "X-User-Role": "ADMIN",
        "X-User-Id": "admin_cmo_01"
    }
    payload = {
        "pre_auth_id": pa_id,
        "override_decision": "APPROVED",
        "override_amount": "30000.00",
        "reason": "Authorized CMO clinical exception",
        "actor_id": "admin_cmo_01"
    }
    response = client.post("/api/v1/admin/preauth/override", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    assert response.json()["is_override"] is True
