"""
Test Suite: AC-04 Pre-Authorization Decision Lifecycle
Acceptance Criteria:
    Pre-auth transitions from PENDING -> APPROVED | PARTIALLY_APPROVED | REJECTED | QUERY_RAISED.
    Every decision requires reason codes.
"""

from decimal import Decimal
import pytest
from src.domain.pre_auth_rule import (
    PreAuthEntity,
    PreAuthDecisionRecord,
    transition_pre_auth_decision,
    InvalidPreAuthTransitionException
)


def test_ac04_allowed_transitions_with_reason_codes():
    """AC-04: Valid transitions from PENDING to standard terminal/review states."""
    pa = PreAuthEntity(
        pre_auth_id="PA-2001",
        claim_id="CLM-3001",
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        diagnosis="ACUTE_APPENDICITIS",
        estimated_cost=Decimal("45000.00"),
        expected_admission_date="2026-10-10",
        status="PENDING"
    )

    decision = transition_pre_auth_decision(
        pa,
        new_status="APPROVED",
        approved_amount=Decimal("45000.00"),
        reason_codes=["AUTO_APPROVED_RULE_01"],
        decider_type="AUTO",
        decider_id="SYSTEM"
    )
    assert pa.status == "APPROVED"
    assert decision.decision == "APPROVED"
    assert decision.approved_amount == Decimal("45000.00")
    assert "AUTO_APPROVED_RULE_01" in decision.reason_codes


def test_ac04_missing_reason_codes_rejected():
    """AC-04: Every decision requires at least one reason code."""
    pa = PreAuthEntity(
        pre_auth_id="PA-2001",
        claim_id="CLM-3001",
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        diagnosis="ACUTE_APPENDICITIS",
        estimated_cost=Decimal("45000.00"),
        expected_admission_date="2026-10-10",
        status="PENDING"
    )
    with pytest.raises(ValueError, match="reason_codes cannot be empty"):
        transition_pre_auth_decision(
            pa,
            new_status="REJECTED",
            approved_amount=Decimal("0.00"),
            reason_codes=[],
            decider_type="AUTO",
            decider_id="SYSTEM"
        )


def test_ac04_invalid_transition_from_rejected():
    """Rule PRE-04: Cannot transition directly from REJECTED without an administrative override."""
    pa = PreAuthEntity(
        pre_auth_id="PA-2001",
        claim_id="CLM-3001",
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        diagnosis="ACUTE_APPENDICITIS",
        estimated_cost=Decimal("45000.00"),
        expected_admission_date="2026-10-10",
        status="REJECTED"
    )
    with pytest.raises(InvalidPreAuthTransitionException):
        transition_pre_auth_decision(
            pa,
            new_status="APPROVED",
            approved_amount=Decimal("45000.00"),
            reason_codes=["DIRECT_APPROVE"],
            decider_type="MANUAL",
            decider_id="DOC_01"
        )
