"""
Domain Layer: Pre-Authorization Rules & Lifecycle (AC-03, AC-04, AC-05)
Enforces submission contracts, state transitions, auto-approval rules,
and immutable decision logging.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional
import uuid


class InvalidPreAuthTransitionException(Exception):
    """Raised when an illegal pre-auth state transition is requested."""
    pass


@dataclass
class PreAuthSubmissionInput:
    """AC-03: Intake contract for hospital pre-authorization submissions."""
    member_id: str
    policy_id: str
    hospital_id: str
    diagnosis: str
    estimated_cost: Decimal
    expected_admission_date: str

    def __post_init__(self):
        if not isinstance(self.estimated_cost, Decimal):
            raise TypeError("estimated_cost must be Decimal")
        if self.estimated_cost <= Decimal("0.00"):
            raise ValueError("estimated_cost must be positive")
        if not self.diagnosis or not self.diagnosis.strip():
            raise ValueError("diagnosis is required")


@dataclass
class PreAuthEntity:
    """Pre-authorization entity representation."""
    pre_auth_id: str
    claim_id: str
    member_id: str
    policy_id: str
    hospital_id: str
    diagnosis: str
    estimated_cost: Decimal
    expected_admission_date: str
    status: str = "PENDING"

    def __post_init__(self):
        if not isinstance(self.estimated_cost, Decimal):
            raise TypeError("estimated_cost must be Decimal")


def create_pre_auth_submission(input_data: PreAuthSubmissionInput) -> PreAuthEntity:
    """AC-03: Factory function creating a PENDING pre-authorization with unique IDs."""
    pre_auth_id = f"PA-{uuid.uuid4().hex[:8].upper()}"
    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    return PreAuthEntity(
        pre_auth_id=pre_auth_id,
        claim_id=claim_id,
        member_id=input_data.member_id,
        policy_id=input_data.policy_id,
        hospital_id=input_data.hospital_id,
        diagnosis=input_data.diagnosis.strip(),
        estimated_cost=input_data.estimated_cost,
        expected_admission_date=input_data.expected_admission_date,
        status="PENDING"
    )


@dataclass
class PreAuthDecisionRecord:
    """AC-04: Immutable decision outcome record."""
    pre_auth_id: str
    decision: str
    approved_amount: Decimal
    reason_codes: List[str]
    decider_type: str = "AUTO"  # AUTO, MANUAL, OVERRIDE
    decider_id: str = "SYSTEM"


VALID_PRE_AUTH_TRANSITIONS = {
    "PENDING": {"APPROVED", "PARTIALLY_APPROVED", "REJECTED", "QUERY_RAISED"},
    "QUERY_RAISED": {"PENDING", "APPROVED", "PARTIALLY_APPROVED", "REJECTED"},
    "PARTIALLY_APPROVED": {"APPROVED", "REJECTED"},
    "APPROVED": set(),  # Terminal in pre-auth phase
    "REJECTED": set(),  # Terminal unless overridden by Admin
}


def transition_pre_auth_decision(
    pre_auth: PreAuthEntity,
    new_status: str,
    approved_amount: Decimal,
    reason_codes: List[str],
    decider_type: str = "AUTO",
    decider_id: str = "SYSTEM"
) -> PreAuthDecisionRecord:
    """AC-04: Transitions pre-auth state and creates immutable decision record."""
    if not isinstance(approved_amount, Decimal):
        raise TypeError("approved_amount must be Decimal")
    if not reason_codes:
        raise ValueError("reason_codes cannot be empty")

    allowed = VALID_PRE_AUTH_TRANSITIONS.get(pre_auth.status, set())
    if new_status not in allowed:
        raise InvalidPreAuthTransitionException(
            f"Cannot transition pre-auth from {pre_auth.status} to {new_status}"
        )

    pre_auth.status = new_status
    return PreAuthDecisionRecord(
        pre_auth_id=pre_auth.pre_auth_id,
        decision=new_status,
        approved_amount=approved_amount,
        reason_codes=reason_codes,
        decider_type=decider_type,
        decider_id=decider_id
    )


@dataclass
class AutoApprovalEngineConfig:
    """Configuration matrix for AC-05 auto-approval engine."""
    cost_threshold: Decimal = Decimal("50000.00")
    auto_approved_diagnoses: List[str] = field(default_factory=lambda: [
        "ACUTE_APPENDICITIS", "CATARACT_SURGERY", "NORMAL_DELIVERY", "HERNIA_REPAIR"
    ])
    exclusions: List[str] = field(default_factory=list)


@dataclass
class AutoApprovalResult:
    """AC-05: Decision outcome of auto-approval evaluation."""
    decision: str
    approved_amount: Decimal
    reason_codes: List[str]


def evaluate_auto_approval(
    diagnosis: str,
    estimated_cost: Decimal,
    remaining_balance: Decimal,
    config: Optional[AutoApprovalEngineConfig] = None
) -> AutoApprovalResult:
    """
    AC-05: Evaluates auto-approval rules.
    - REJECTED if diagnosis in exclusions.
    - QUERY_RAISED if estimated_cost > threshold or diagnosis not in whitelist.
    - REJECTED if remaining_balance <= 0.
    - PARTIALLY_APPROVED if estimated_cost > remaining_balance.
    - APPROVED if cost <= threshold, diagnosis in whitelist, and cost <= balance.
    """
    if config is None:
        config = AutoApprovalEngineConfig()

    diag_norm = diagnosis.strip().upper()
    exclusions_norm = [e.strip().upper() for e in config.exclusions]
    whitelist_norm = [w.strip().upper() for w in config.auto_approved_diagnoses]

    # Check 1: Excluded condition
    if diag_norm in exclusions_norm:
        return AutoApprovalResult(
            decision="REJECTED",
            approved_amount=Decimal("0.00"),
            reason_codes=["EXCLUDED_CONDITION"]
        )

    # Check 2: Exceeds auto-approval monetary threshold
    if estimated_cost > config.cost_threshold:
        return AutoApprovalResult(
            decision="QUERY_RAISED",
            approved_amount=Decimal("0.00"),
            reason_codes=["THRESHOLD_EXCEEDED_MANUAL_REVIEW"]
        )

    # Check 3: Whitelist check
    if diag_norm not in whitelist_norm:
        return AutoApprovalResult(
            decision="QUERY_RAISED",
            approved_amount=Decimal("0.00"),
            reason_codes=["MANUAL_ADJUDICATION_REQUIRED"]
        )

    # Check 4: Policy balance exhausted
    if remaining_balance <= Decimal("0.00"):
        return AutoApprovalResult(
            decision="REJECTED",
            approved_amount=Decimal("0.00"),
            reason_codes=["SUM_INSURED_EXHAUSTED"]
        )

    # Check 5: Partial approval due to balance cap
    if estimated_cost > remaining_balance:
        return AutoApprovalResult(
            decision="PARTIALLY_APPROVED",
            approved_amount=remaining_balance,
            reason_codes=["POLICY_BALANCE_CAPPED"]
        )

    # All criteria satisfied: Full Auto-Approval
    return AutoApprovalResult(
        decision="APPROVED",
        approved_amount=estimated_cost,
        reason_codes=["AUTO_APPROVED_RULE_01"]
    )
