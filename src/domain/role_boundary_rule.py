"""
Domain Layer: Role Boundaries & Authorization Rules (Section 8)
Enforces multi-tenancy and role access boundaries:
- CUSTOMER: can only access own cases/policies
- HOSPITAL: can only access its own cases; cannot access another hospital's cases
- INSURER: can review relevant claims/pre-auths
- ADMIN: can execute authorized administrative overrides
"""

from enum import Enum
from typing import List


class Role(str, Enum):
    CUSTOMER = "CUSTOMER"
    HOSPITAL = "HOSPITAL"
    INSURER = "INSURER"
    ADMIN = "ADMIN"


class AccessDeniedException(Exception):
    """Raised when actor attempts to breach multi-tenant or role boundaries."""
    pass


def authorize_role(actor_role: str, allowed_roles: List[Role]) -> bool:
    """Validates that actor possesses one of the authorized roles."""
    allowed_str = {r.value for r in allowed_roles}
    if actor_role not in allowed_str:
        raise AccessDeniedException(
            f"Access denied for role '{actor_role}'. Required roles: {list(allowed_str)}"
        )
    return True


def authorize_hospital_tenant(actor_hospital_id: str, target_hospital_id: str) -> bool:
    """Enforces hospital multi-tenancy: a hospital cannot access another hospital's data."""
    if not actor_hospital_id or not target_hospital_id:
        raise AccessDeniedException("Hospital tenant identifier missing")
    if actor_hospital_id.strip() != target_hospital_id.strip():
        raise AccessDeniedException(
            f"Hospital tenant violation: {actor_hospital_id} cannot access case owned by {target_hospital_id}"
        )
    return True


def authorize_customer_tenant(actor_member_id: str, target_member_id: str) -> bool:
    """Enforces customer multi-tenancy: customer can only query their own policy/claims."""
    if not actor_member_id or not target_member_id:
        raise AccessDeniedException("Customer tenant identifier missing")
    if actor_member_id.strip() != target_member_id.strip():
        raise AccessDeniedException(
            f"Customer tenant violation: {actor_member_id} cannot access records of {target_member_id}"
        )
    return True
