"""
Test Suite: AC-02 Network Hospital Eligibility Lookup
Acceptance Criteria:
    Network hospital can look up customer eligibility using member_id and policy_id.
    System must return ELIGIBLE or NOT_ELIGIBLE with reason codes.
"""

from decimal import Decimal
import pytest
from src.domain.eligibility_rule import (
    EligibilityCheckInput,
    EligibilityEvaluationResult,
    evaluate_member_eligibility
)


def test_ac02_eligible_customer_lookup():
    """AC-02: Returns ELIGIBLE for active member at an in-network hospital with positive balance."""
    payload = EligibilityCheckInput(
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        is_policy_active=True,
        is_hospital_in_network=True,
        remaining_balance=Decimal("350000.00")
    )
    result: EligibilityEvaluationResult = evaluate_member_eligibility(payload)
    assert result.status == "ELIGIBLE"
    assert result.is_eligible is True
    assert result.reason_codes == []
    assert result.available_balance == Decimal("350000.00")


def test_ac02_not_eligible_hospital_out_of_network():
    """AC-02: Returns NOT_ELIGIBLE with HOSP_OUT_OF_NETWORK when hospital is not in-network."""
    payload = EligibilityCheckInput(
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-999",
        is_policy_active=True,
        is_hospital_in_network=False,
        remaining_balance=Decimal("350000.00")
    )
    result = evaluate_member_eligibility(payload)
    assert result.status == "NOT_ELIGIBLE"
    assert result.is_eligible is False
    assert "HOSP_OUT_OF_NETWORK" in result.reason_codes


def test_ac02_not_eligible_inactive_policy():
    """AC-02: Returns NOT_ELIGIBLE with POL_INACTIVE when policy has lapsed or expired."""
    payload = EligibilityCheckInput(
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        is_policy_active=False,
        is_hospital_in_network=True,
        remaining_balance=Decimal("350000.00")
    )
    result = evaluate_member_eligibility(payload)
    assert result.status == "NOT_ELIGIBLE"
    assert "POL_INACTIVE" in result.reason_codes


def test_ac02_not_eligible_exhausted_sum_insured():
    """AC-02: Returns NOT_ELIGIBLE with SUM_INSURED_EXHAUSTED when balance is zero."""
    payload = EligibilityCheckInput(
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-001",
        is_policy_active=True,
        is_hospital_in_network=True,
        remaining_balance=Decimal("0.00")
    )
    result = evaluate_member_eligibility(payload)
    assert result.status == "NOT_ELIGIBLE"
    assert "SUM_INSURED_EXHAUSTED" in result.reason_codes


def test_ac02_cumulative_failure_reasons():
    """AC-02: Accurately reports multiple reason codes if multiple checks fail simultaneously."""
    payload = EligibilityCheckInput(
        member_id="MEM-1001",
        policy_id="POL-5001",
        hospital_id="HOSP-999",
        is_policy_active=False,
        is_hospital_in_network=False,
        remaining_balance=Decimal("0.00")
    )
    result = evaluate_member_eligibility(payload)
    assert result.status == "NOT_ELIGIBLE"
    assert "HOSP_OUT_OF_NETWORK" in result.reason_codes
    assert "POL_INACTIVE" in result.reason_codes
    assert "SUM_INSURED_EXHAUSTED" in result.reason_codes
