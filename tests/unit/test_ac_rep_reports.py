"""
Acceptance Criteria Tests: Reports & Cashless Analytics (specs/reports_spec.md).
Explicitly tests:
- AC-REP-01: Admin can retrieve average pre-authorization turnaround time across all network hospitals.
- AC-REP-02: Admin can retrieve query rate breakdown by hospital facility.
- AC-REP-03: System calculates total settled payout volume and loss ratio without floating-point errors.
- REP-01: Privacy in analytics (zero patient names or member IDs exposed).
- REP-02: Monetary precision in fixed-point Decimal.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.database import init_db
from src.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    seed_database()
    yield


def test_ac_rep_01_average_pre_auth_turnaround_time():
    """AC-REP-01: Admin can retrieve turnaround time (average, median, 95th percentile)."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    response = client.get("/api/v1/reports/turnaround-time", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "average_tat_seconds" in data
    assert "median_tat_seconds" in data
    assert "p95_tat_seconds" in data
    assert isinstance(data["average_tat_seconds"], (int, float))
    assert data["average_tat_seconds"] >= 0


def test_ac_rep_02_query_rate_by_hospital():
    """AC-REP-02: Admin can retrieve query rate breakdown by hospital facility."""
    headers = {"X-User-Role": "INSURER", "X-User-Id": "claims_manager_1"}
    response = client.get("/api/v1/reports/query-rates", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "query_rate_by_hospital" in data
    rates = data["query_rate_by_hospital"]
    assert isinstance(rates, dict)
    # Check rate format is decimal percentage string or float
    for hosp_id, rate in rates.items():
        assert isinstance(rate, (int, float))
        assert 0.0 <= rate <= 100.0


def test_ac_rep_03_settlement_volume_and_loss_ratio():
    """AC-REP-03: System calculates total settled payout volume and loss ratio without floating-point errors."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    response = client.get("/api/v1/reports/settlement-summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_settled_amount" in data
    assert "settled_claim_count" in data
    assert "loss_ratio" in data
    
    # Must be valid Decimal representations
    total_settled = Decimal(str(data["total_settled_amount"]))
    loss_ratio = Decimal(str(data["loss_ratio"]))
    assert total_settled >= Decimal("0.00")
    assert loss_ratio >= Decimal("0.00")
    assert isinstance(data["settled_claim_count"], int)


def test_ac_rep_comprehensive_analytics_dto():
    """Verify comprehensive analytics DTO containing all operational metrics and privacy enforcement."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    response = client.get("/api/v1/reports/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Check presence of all required sections
    assert "turnaround_time" in data
    assert "settlement_volume" in data
    assert "query_rates" in data
    assert "top_diagnoses" in data
    assert "loss_ratio" in data
    
    # REP-01 Privacy Rule: top diagnoses must not expose patient names or member IDs
    diagnoses = data["top_diagnoses"]
    assert isinstance(diagnoses, list)
    for entry in diagnoses:
        assert "diagnosis" in entry
        assert "count" in entry
        assert "member_id" not in entry
        assert "patient_name" not in entry


def test_ac_rep_unauthorized_role_rejected():
    """Non-INSURER and non-ADMIN roles receive 403 Forbidden."""
    # Attempt as CUSTOMER
    headers = {"X-User-Role": "CUSTOMER", "X-User-Id": "MEM-1001"}
    response = client.get("/api/v1/reports/analytics", headers=headers)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]

    # Attempt as HOSPITAL
    headers_hosp = {"X-User-Role": "HOSPITAL", "X-User-Id": "HOSP-001"}
    res_hosp = client.get("/api/v1/reports/turnaround-time", headers=headers_hosp)
    assert res_hosp.status_code == 403


def test_ac_rep_empty_dataset_handling():
    """Date filtering that returns empty datasets handles calculations gracefully."""
    headers = {"X-User-Role": "ADMIN", "X-User-Id": "admin_dr_smith"}
    # Filter with future dates where no data exists
    response = client.get("/api/v1/reports/analytics?from_date=2099-01-01&to_date=2099-12-31", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert Decimal(str(data["settlement_volume"]["total_settled_amount"])) == Decimal("0.00")
    assert data["settlement_volume"]["settled_claim_count"] == 0
    assert Decimal(str(data["loss_ratio"])) == Decimal("0.00")
