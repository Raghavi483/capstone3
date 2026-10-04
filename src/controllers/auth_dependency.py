"""
Authentication and Role-Based Authorization Dependencies (Priority 4, Section 8, NFR-04).
Enforces real controller-level role verification without insecure default admin fallbacks.
"""

from dataclasses import dataclass
from typing import Optional
from fastapi import Header, HTTPException, status


@dataclass
class AuthContext:
    user_id: Optional[str] = None
    role: Optional[str] = None
    hospital_id: Optional[str] = None
    member_id: Optional[str] = None


def get_current_user_context(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_hospital_id: Optional[str] = Header(None, alias="X-Hospital-Id"),
    x_member_id: Optional[str] = Header(None, alias="X-Member-Id")
) -> AuthContext:
    """Extract authenticated context from headers."""
    return AuthContext(
        user_id=x_user_id,
        role=x_user_role.upper() if x_user_role else None,
        hospital_id=x_hospital_id,
        member_id=x_member_id
    )


def require_admin(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
) -> str:
    """
    Enforces that caller is an authenticated ADMIN.
    Raises 401 if unauthenticated, 403 if role is not ADMIN.
    """
    if not x_user_id and not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing credentials."
        )
    if not x_user_role or x_user_role.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required. Only ADMIN role can execute overrides."
        )
    return x_user_id or "ADMIN"


def verify_customer_tenancy(
    target_member_id: str,
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_member_id: Optional[str] = Header(None, alias="X-Member-Id"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> None:
    """
    Ensures a CUSTOMER can only inspect their own member data.
    """
    if x_user_role and x_user_role.upper() == "CUSTOMER":
        effective_member = x_member_id or x_user_id
        if effective_member and effective_member != target_member_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Customer '{effective_member}' cannot access data of '{target_member_id}'."
            )


def verify_hospital_tenancy(
    target_hospital_id: str,
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_hospital_id: Optional[str] = Header(None, alias="X-Hospital-Id")
) -> None:
    """
    Ensures a HOSPITAL cannot manipulate claims for another hospital.
    """
    if x_user_role and x_user_role.upper() == "HOSPITAL":
        if x_hospital_id and x_hospital_id != target_hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Hospital '{x_hospital_id}' cannot operate on facility '{target_hospital_id}'."
            )
