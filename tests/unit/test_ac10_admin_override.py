"""
Test Suite: AC-10 Insurer Admin Override
Acceptance Criteria:
    Insurer admin can override auto-rejected or query-raised pre-auths.
    Requires authorized role (ADMIN), non-empty reason, and audit logging.
    Amount cannot exceed policy remaining balance.
"""

from decimal import Decimal
import pytest
from src.domain.adjudication_rule import (
    AdminOverrideInput,
    evaluate_admin_override,
    AdminOverrideResult,
    UnauthorizedOverrideException
)


def test_ac10_admin_override_success():
    """AC-10 Scenario 1: Admin successfully overrides rejected pre-auth."""
    override_input = AdminOverrideInput(
        pre_auth_id="PA-2002",
        current_status="REJECTED",
        override_decision="APPROVED",
        override_amount=Decimal("50000.00"),
        policy_balance=Decimal("100000.00"),
        reason="Exceptional clinical necessity approved by medical director",
        actor_role="ADMIN",
        actor_id="admin_user_01"
    )
    result: AdminOverrideResult = evaluate_admin_override(override_input)
    assert result.new_status == "APPROVED"
    assert result.authorized_amount == Decimal("50000.00")
    assert result.is_override is True
    assert "ADMIN_OVERRIDE_APPLIED" in result.reason_codes


def test_ac10_non_admin_role_forbidden():
    """AC-10 Scenario 2: Hospital or customer role attempting override raises UnauthorizedOverrideException."""
    override_input = AdminOverrideInput(
        pre_auth_id="PA-2002",
        current_status="REJECTED",
        override_decision="APPROVED",
        override_amount=Decimal("50000.00"),
        policy_balance=Decimal("100000.00"),
        reason="Trying to override own pre-auth",
        actor_role="HOSPITAL",  # Unauthorized role
        actor_id="hosp_user_01"
    )
    with pytest.raises(UnauthorizedOverrideException, match="Only ADMIN role can execute overrides"):
        evaluate_admin_override(override_input)


def test_ac10_empty_reason_rejected():
    """AC-10 Scenario 3: Missing or short justification (<10 chars) raises ValueError."""
    with pytest.raises(ValueError, match="Override reason must be at least 10 characters"):
        AdminOverrideInput(
            pre_auth_id="PA-2002",
            current_status="REJECTED",
            override_decision="APPROVED",
            override_amount=Decimal("50000.00"),
            policy_balance=Decimal("100000.00"),
            reason="Short",  # Too short
            actor_role="ADMIN",
            actor_id="admin_user_01"
        )


def test_ac10_override_cannot_exceed_remaining_balance():
    """AC-10 Invariant: Override amount cannot exceed available policy balance."""
    override_input = AdminOverrideInput(
        pre_auth_id="PA-2002",
        current_status="REJECTED",
        override_decision="APPROVED",
        override_amount=Decimal("150000.00"),  # Exceeds balance
        policy_balance=Decimal("100000.00"),
        reason="Attempting to approve more than policy balance",
        actor_role="ADMIN",
        actor_id="admin_user_01"
    )
    with pytest.raises(ValueError, match="Override amount cannot exceed policy remaining balance"):
        evaluate_admin_override(override_input)
