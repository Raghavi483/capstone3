"""
Unit Tests: Policy Rule Versioning and Historical Claim Invariance (Priority 3B, NET-02).
Proves:
1. Historical claims remain bound to their original policy rule version.
2. Publishing a new policy version modifies future claims without altering past claims.
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.database import SessionLocal, init_db
from src.repositories.models import PolicyRuleVersionModel, ClaimModel, PreAuthModel
from src.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    seed_database(force=True)
    yield


def test_historical_claim_remains_bound_to_prior_policy_version():
    """
    Priority 3B / NET-02:
    - Claim 1 under v1.0.0 (threshold = $50,000) is auto-approved.
    - Admin publishes v2.0.0 with threshold = $20,000.
    - Claim 2 under v2.0.0 for $35,000 is NOT auto-approved (QUERY_RAISED).
    - Claim 1 retains v1.0.0 and remains APPROVED.
    """
    db = SessionLocal()
    try:
        # Step 1: Submit Claim 1 for $45,000 (Eligible under v1.0.0 threshold of $50,000)
        res1 = client.post("/api/v1/preauth/submit", json={
            "member_id": "MEM-1001",
            "policy_id": "POL-5001",
            "hospital_id": "HOSP-001",
            "diagnosis": "ACUTE_APPENDICITIS",
            "estimated_cost": "45000.00",
            "expected_admission_date": "2026-11-01"
        })
        assert res1.status_code == 201
        data1 = res1.json()
        assert data1["status"] == "APPROVED"
        pa_id_1 = data1["pre_auth_id"]
        claim_id_1 = data1["claim_id"]

        pa_rec_1 = db.query(PreAuthModel).filter_by(pre_auth_id=pa_id_1).first()
        assert pa_rec_1.policy_version_tag == "v1.0.0"

        # Step 2: Publish new policy version v2.0.0 with reduced threshold of $20,000
        # Deactivate v1.0.0
        v1 = db.query(PolicyRuleVersionModel).filter_by(version_id="POL-5001-v1.0.0").first()
        if v1:
            v1.is_active = False

        v2 = PolicyRuleVersionModel(
            version_id="POL-5001-v2.0.0",
            policy_code="POL-5001",
            version_tag="v2.0.0",
            effective_from="2026-11-15",
            auto_approval_threshold=Decimal("20000.00"),  # Strict threshold
            buffer_percentage=Decimal("0.10"),
            policy_cap=Decimal("500000.00"),
            auto_approved_diagnoses=["ACUTE_APPENDICITIS"],
            exclusions=["COSMETIC_SURGERY"],
            is_active=True
        )
        db.add(v2)
        db.commit()

        # Step 3: Submit Claim 2 for $35,000 (Exceeds v2.0.0 threshold of $20,000)
        res2 = client.post("/api/v1/preauth/submit", json={
            "member_id": "MEM-1001",
            "policy_id": "POL-5001",
            "hospital_id": "HOSP-001",
            "diagnosis": "ACUTE_APPENDICITIS",
            "estimated_cost": "35000.00",
            "expected_admission_date": "2026-11-20"
        })
        assert res2.status_code == 201
        data2 = res2.json()
        # Must NOT be auto-approved under v2.0.0
        assert data2["status"] == "QUERY_RAISED"
        assert "THRESHOLD_EXCEEDED_MANUAL_REVIEW" in data2["reason_codes"]
        pa_id_2 = data2["pre_auth_id"]

        pa_rec_2 = db.query(PreAuthModel).filter_by(pre_auth_id=pa_id_2).first()
        assert pa_rec_2.policy_version_tag == "v2.0.0"

        # Step 4: Verify Claim 1 remains intact, bound to v1.0.0, and status APPROVED
        db.expire_all()
        pa_rec_1_reloaded = db.query(PreAuthModel).filter_by(pre_auth_id=pa_id_1).first()
        assert pa_rec_1_reloaded.status == "APPROVED"
        assert pa_rec_1_reloaded.policy_version_tag == "v1.0.0"

        claim_rec_1 = db.query(ClaimModel).filter_by(claim_id=claim_id_1).first()
        assert claim_rec_1.policy_version_tag == "v1.0.0"
    finally:
        db.close()
