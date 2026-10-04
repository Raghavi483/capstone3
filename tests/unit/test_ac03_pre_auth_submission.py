"""
Test Suite: AC-03 Pre-Authorization Request Submission
Acceptance Criteria:
    Network hospital submits pre-auth with diagnosis, estimated_cost, and expected admission date.
    Initial state must be PENDING.
"""

from decimal import Decimal
import pytest
from src.domain.pre_auth_rule import (
    PreAuthSubmissionInput,
    PreAuthEntity,
    create_pre_auth_submission
)


def test_ac03_submission_initial_pending_state():
    """AC-03: Submitting pre-authorization initializes state to PENDING."""
    submission = PreAuthSubmissionInput(
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        diagnosis="CHOLECYSTITIS",
        estimated_cost=Decimal("60000.00"),
        expected_admission_date="2026-10-12"
    )
    entity: PreAuthEntity = create_pre_auth_submission(submission)
    assert entity.status == "PENDING"
    assert entity.pre_auth_id.startswith("PA-")
    assert entity.claim_id.startswith("CLM-")
    assert entity.estimated_cost == Decimal("60000.00")
    assert entity.diagnosis == "CHOLECYSTITIS"


def test_ac03_submission_float_rejection():
    """NFR-01: Prohibits float for estimated_cost."""
    with pytest.raises(TypeError, match="estimated_cost must be Decimal"):
        PreAuthSubmissionInput(
            member_id="MEM-1001",
            policy_id="POL-5001",
            hospital_id="HOSP-001",
            diagnosis="CHOLECYSTITIS",
            estimated_cost=60000.00,  # float violation
            expected_admission_date="2026-10-12"
        )


def test_ac03_submission_positive_cost_required():
    """Rule PRE-01: Estimated cost must be strictly positive."""
    with pytest.raises(ValueError, match="estimated_cost must be positive"):
        PreAuthSubmissionInput(
            member_id="MEM-1001",
            policy_id="POL-5001",
            hospital_id="HOSP-001",
            diagnosis="CHOLECYSTITIS",
            estimated_cost=Decimal("0.00"),
            expected_admission_date="2026-10-12"
        )
