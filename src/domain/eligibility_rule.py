"""
Domain Layer: Eligibility & Policy Coverage Rules (AC-01, AC-02)
Enforces business rules for customer policy coverage, exclusions,
and hospital eligibility adjudication.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class CustomerPolicyCoverage:
    """AC-01: Encapsulates customer policy coverage parameters with Decimal precision."""
    member_id: str
    policy_id: str
    product_name: str
    sum_insured: Decimal
    remaining_balance: Decimal
    exclusions: List[str] = field(default_factory=list)
    network_hospitals: List[str] = field(default_factory=list)
    is_active: bool = True

    def __post_init__(self):
        if not isinstance(self.sum_insured, Decimal):
            raise TypeError("sum_insured must be Decimal")
        if not isinstance(self.remaining_balance, Decimal):
            raise TypeError("remaining_balance must be Decimal")
        if self.sum_insured < Decimal("0.00"):
            raise ValueError("sum_insured cannot be negative")


class PolicyExclusionRule:
    """AC-01: Evaluates whether a diagnosis or condition is excluded under the policy."""
    def __init__(self, exclusions: List[str]):
        self.exclusions = [e.strip().upper() for e in exclusions]

    def is_excluded(self, diagnosis: str) -> bool:
        if not diagnosis:
            return False
        normalized = diagnosis.strip().upper()
        return normalized in self.exclusions


@dataclass
class EligibilityCheckInput:
    """AC-02: Input contract for network hospital eligibility lookup."""
    member_id: str
    policy_id: str
    hospital_id: str
    is_policy_active: bool
    is_hospital_in_network: bool
    remaining_balance: Decimal

    def __post_init__(self):
        if not isinstance(self.remaining_balance, Decimal):
            raise TypeError("remaining_balance must be Decimal")


@dataclass
class EligibilityEvaluationResult:
    """AC-02: Output contract of eligibility determination with standardized reason codes."""
    status: str
    is_eligible: bool
    reason_codes: List[str]
    available_balance: Decimal


def evaluate_member_eligibility(payload: EligibilityCheckInput) -> EligibilityEvaluationResult:
    """
    AC-02: Core domain rule for member eligibility determination.
    Returns ELIGIBLE or NOT_ELIGIBLE with reason codes.
    Rules:
    - HOSP_OUT_OF_NETWORK if querying hospital is not in-network.
    - POL_INACTIVE if policy is lapsed/inactive.
    - SUM_INSURED_EXHAUSTED if remaining balance <= 0.00.
    """
    reasons: List[str] = []

    if not payload.is_hospital_in_network:
        reasons.append("HOSP_OUT_OF_NETWORK")

    if not payload.is_policy_active:
        reasons.append("POL_INACTIVE")

    if payload.remaining_balance <= Decimal("0.00"):
        reasons.append("SUM_INSURED_EXHAUSTED")

    if reasons:
        return EligibilityEvaluationResult(
            status="NOT_ELIGIBLE",
            is_eligible=False,
            reason_codes=reasons,
            available_balance=payload.remaining_balance
        )

    return EligibilityEvaluationResult(
        status="ELIGIBLE",
        is_eligible=True,
        reason_codes=[],
        available_balance=payload.remaining_balance
    )
