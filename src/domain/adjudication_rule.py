"""
Domain Layer: Adjudication & Admin Override Rules (AC-10)
Enforces security role boundaries, justification validity,
and policy balance caps on administrator overrides.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Any


class UnauthorizedOverrideException(Exception):
    """Raised when non-admin actor attempts an administrative override."""
    pass


@dataclass
class AdminOverrideInput:
    """AC-10: Input contract for administrator override."""
    pre_auth_id: str
    current_status: str
    override_decision: str  # APPROVED | PARTIALLY_APPROVED
    override_amount: Decimal
    policy_balance: Decimal
    reason: str
    actor_role: str
    actor_id: str

    def __post_init__(self):
        if not isinstance(self.override_amount, Decimal):
            raise TypeError("override_amount must be Decimal")
        if not isinstance(self.policy_balance, Decimal):
            raise TypeError("policy_balance must be Decimal")
        if not self.reason or len(self.reason.strip()) < 10:
            raise ValueError("Override reason must be at least 10 characters")
        if self.override_decision not in {"APPROVED", "PARTIALLY_APPROVED"}:
            raise ValueError(f"Invalid override decision: {self.override_decision}")


@dataclass
class AdminOverrideResult:
    """AC-10: Outcome of administrator override evaluation."""
    pre_auth_id: str
    new_status: str
    authorized_amount: Decimal
    is_override: bool
    reason_codes: List[str]
    actor_id: str
    audit_payload: Dict[str, Any]


def evaluate_admin_override(payload: AdminOverrideInput) -> AdminOverrideResult:
    """
    AC-10: Enforces override rules.
    - Only ADMIN role allowed.
    - Status must be eligible for override (REJECTED or QUERY_RAISED).
    - Amount cannot exceed policy remaining balance.
    """
    if payload.actor_role not in {"ADMIN", "INSURER_ADMIN"}:
        raise UnauthorizedOverrideException("Only ADMIN role can execute overrides")

    if payload.current_status not in {"REJECTED", "QUERY_RAISED"}:
        raise ValueError(
            f"Cannot override pre-authorization with status {payload.current_status}"
        )

    if payload.override_amount > payload.policy_balance:
        raise ValueError("Override amount cannot exceed policy remaining balance")

    audit_payload = {
        "pre_auth_id": payload.pre_auth_id,
        "previous_status": payload.current_status,
        "override_decision": payload.override_decision,
        "authorized_amount": str(payload.override_amount),
        "justification": payload.reason.strip(),
        "actor_role": payload.actor_role,
        "actor_id": payload.actor_id
    }

    return AdminOverrideResult(
        pre_auth_id=payload.pre_auth_id,
        new_status=payload.override_decision,
        authorized_amount=payload.override_amount,
        is_override=True,
        reason_codes=["ADMIN_OVERRIDE_APPLIED"],
        actor_id=payload.actor_id,
        audit_payload=audit_payload
    )
