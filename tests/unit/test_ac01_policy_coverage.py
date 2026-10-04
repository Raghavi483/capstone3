"""
Test Suite: AC-01 Customer Registration and Policy Coverage
Acceptance Criteria:
    Customer can register and link to their health policy.
    Coverage details must be visible including:
    - sum insured (Decimal)
    - exclusions
    - network hospitals
"""

from decimal import Decimal
import pytest
from src.domain.eligibility_rule import CustomerPolicyCoverage, PolicyExclusionRule


def test_ac01_customer_policy_coverage_structure():
    """AC-01: Validates customer policy coverage details structure and Decimal types."""
    coverage = CustomerPolicyCoverage(
        member_id="MEM-1001",
        policy_id="POL-5001",
        product_name="MediCard Gold Health Plan",
        sum_insured=Decimal("500000.00"),
        remaining_balance=Decimal("500000.00"),
        exclusions=["COSMETIC_SURGERY", "EXPERIMENTAL_TREATMENT", "DENTAL_UNLESS_ACCIDENT"],
        network_hospitals=["HOSP-001", "HOSP-002", "HOSP-003"],
        is_active=True
    )
    assert coverage.member_id == "MEM-1001"
    assert coverage.policy_id == "POL-5001"
    assert isinstance(coverage.sum_insured, Decimal)
    assert coverage.sum_insured == Decimal("500000.00")
    assert "COSMETIC_SURGERY" in coverage.exclusions
    assert "HOSP-001" in coverage.network_hospitals
    assert coverage.is_active is True


def test_ac01_sum_insured_float_rejection():
    """NFR-01: Prohibits floating point types for sum_insured to prevent precision drift."""
    with pytest.raises(TypeError, match="must be Decimal"):
        CustomerPolicyCoverage(
            member_id="MEM-1001",
            policy_id="POL-5001",
            product_name="MediCard Gold",
            sum_insured=500000.00,  # float violation
            remaining_balance=Decimal("500000.00"),
            exclusions=[],
            network_hospitals=[],
            is_active=True
        )


def test_ac01_exclusion_rule_evaluation():
    """AC-01: Checks whether diagnosis is prohibited by policy exclusions."""
    rule = PolicyExclusionRule(exclusions=["COSMETIC_SURGERY", "HAIR_TRANSPLANT"])
    assert rule.is_excluded("Cosmetic_Surgery") is True
    assert rule.is_excluded("ACUTE_APPENDICITIS") is False
