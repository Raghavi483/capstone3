"""
Test Suite: AC-05 Automatic Approval Engine
Acceptance Criteria:
    Auto-approves pre-auth when:
    - estimated_cost <= configured threshold (INR 50,000.00)
    - diagnosis is in auto-approved whitelist
    - policy balance cap is not exceeded.
"""

from decimal import Decimal
import pytest
from src.domain.pre_auth_rule import (
    AutoApprovalEngineConfig,
    evaluate_auto_approval,
    AutoApprovalResult
)


@pytest.fixture
def rule_config():
    return AutoApprovalEngineConfig(
        cost_threshold=Decimal("50000.00"),
        auto_approved_diagnoses=["ACUTE_APPENDICITIS", "CATARACT_SURGERY", "NORMAL_DELIVERY", "HERNIA_REPAIR"],
        exclusions=["COSMETIC_SURGERY", "EXPERIMENTAL_TREATMENT"]
    )


def test_ac05_auto_approval_criteria_met(rule_config):
    """AC-05: Returns APPROVED when all three criteria are satisfied."""
    result: AutoApprovalResult = evaluate_auto_approval(
        diagnosis="ACUTE_APPENDICITIS",
        estimated_cost=Decimal("45000.00"),
        remaining_balance=Decimal("200000.00"),
        config=rule_config
    )
    assert result.decision == "APPROVED"
    assert result.approved_amount == Decimal("45000.00")
    assert "AUTO_APPROVED_RULE_01" in result.reason_codes


def test_ac05_auto_reject_if_diagnosis_excluded(rule_config):
    """AC-05: Returns REJECTED with EXCLUDED_CONDITION if diagnosis is in exclusions."""
    result = evaluate_auto_approval(
        diagnosis="COSMETIC_SURGERY",
        estimated_cost=Decimal("30000.00"),
        remaining_balance=Decimal("200000.00"),
        config=rule_config
    )
    assert result.decision == "REJECTED"
    assert result.approved_amount == Decimal("0.00")
    assert "EXCLUDED_CONDITION" in result.reason_codes


def test_ac05_partial_approval_when_balance_less_than_cost(rule_config):
    """AC-05: Returns PARTIALLY_APPROVED when cost <= threshold but > remaining balance."""
    result = evaluate_auto_approval(
        diagnosis="CATARACT_SURGERY",
        estimated_cost=Decimal("40000.00"),
        remaining_balance=Decimal("25000.00"),
        config=rule_config
    )
    assert result.decision == "PARTIALLY_APPROVED"
    assert result.approved_amount == Decimal("25000.00")
    assert "POLICY_BALANCE_CAPPED" in result.reason_codes


def test_ac05_query_raised_when_diagnosis_not_in_whitelist(rule_config):
    """AC-05: Returns QUERY_RAISED for unlisted diagnosis requiring clinical review."""
    result = evaluate_auto_approval(
        diagnosis="UNSPECIFIED_ABDOMINAL_PAIN",
        estimated_cost=Decimal("40000.00"),
        remaining_balance=Decimal("200000.00"),
        config=rule_config
    )
    assert result.decision == "QUERY_RAISED"
    assert result.approved_amount == Decimal("0.00")
    assert "MANUAL_ADJUDICATION_REQUIRED" in result.reason_codes


def test_ac05_query_raised_when_cost_exceeds_threshold(rule_config):
    """AC-05: Returns QUERY_RAISED when estimated cost exceeds auto threshold (> 50,000)."""
    result = evaluate_auto_approval(
        diagnosis="ACUTE_APPENDICITIS",
        estimated_cost=Decimal("75000.00"),
        remaining_balance=Decimal("200000.00"),
        config=rule_config
    )
    assert result.decision == "QUERY_RAISED"
    assert result.approved_amount == Decimal("0.00")
    assert "THRESHOLD_EXCEEDED_MANUAL_REVIEW" in result.reason_codes
