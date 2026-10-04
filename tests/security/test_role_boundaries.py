"""
Test Suite: Security & Role Boundaries (Section 8)
Verifies multi-tenancy and role access enforcement:
- Customer can access own cases/policies; cannot access another customer's data
- Hospital can access only its own cases; cannot access another hospital's case
- Insurer can review claims and pre-authorizations
- Admin can perform authorized overrides; non-admin cannot
"""

import pytest
from src.domain.role_boundary_rule import (
    Role,
    authorize_role,
    authorize_hospital_tenant,
    authorize_customer_tenant,
    AccessDeniedException
)


def test_role_customer_can_only_access_own_data():
    """Section 8: Customer access succeeds for own member_id."""
    assert authorize_customer_tenant(actor_member_id="MEM-1001", target_member_id="MEM-1001") is True


def test_role_customer_accessing_other_customer_fails():
    """Section 8: Customer attempting to access another customer's record raises AccessDeniedException."""
    with pytest.raises(AccessDeniedException, match="Customer tenant violation"):
        authorize_customer_tenant(actor_member_id="MEM-1001", target_member_id="MEM-1002")


def test_role_hospital_can_only_access_own_cases():
    """Section 8: Hospital access succeeds for own hospital_id."""
    assert authorize_hospital_tenant(actor_hospital_id="HOSP-001", target_hospital_id="HOSP-001") is True


def test_role_hospital_accessing_other_hospital_case_fails():
    """Section 8: Hospital attempting to query another hospital's case raises AccessDeniedException."""
    with pytest.raises(AccessDeniedException, match="Hospital tenant violation"):
        authorize_hospital_tenant(actor_hospital_id="HOSP-001", target_hospital_id="HOSP-002")


def test_role_admin_authorized_for_overrides():
    """Section 8: Admin role passes override authorization."""
    assert authorize_role("ADMIN", [Role.ADMIN]) is True


def test_role_non_admin_fails_override():
    """Section 8: Non-admin roles (HOSPITAL, CUSTOMER) fail override authorization."""
    with pytest.raises(AccessDeniedException, match="Access denied for role 'HOSPITAL'"):
        authorize_role("HOSPITAL", [Role.ADMIN])

    with pytest.raises(AccessDeniedException, match="Access denied for role 'CUSTOMER'"):
        authorize_role("CUSTOMER", [Role.ADMIN])


def test_role_insurer_can_review_claims():
    """Section 8: Insurer and Admin roles pass review authorization."""
    assert authorize_role("INSURER", [Role.INSURER, Role.ADMIN]) is True
    assert authorize_role("ADMIN", [Role.INSURER, Role.ADMIN]) is True
