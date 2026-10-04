"""
Controller: Network Hospital & Policy Administration Endpoints.
Enforces NFR-04 role boundaries (only ADMIN permitted).
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.repositories.database import get_db
from src.services.network_admin_service import NetworkAdminService
from src.domain.network_admin_rule import (
    InvalidHospitalPayloadException,
    InvalidPolicyConfigurationException
)

router = APIRouter(prefix="/api/v1/admin", tags=["Network & Policy Administration"])


def verify_admin_role(x_user_role: Optional[str] = Header(None, alias="X-User-Role")):
    """Ensure caller has ADMIN role."""
    if not x_user_role or x_user_role.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin role required for network administration."
        )


class OnboardHospitalRequest(BaseModel):
    hospital_id: str
    name: str
    tier: str = Field(default="TIER_1")
    city: str
    state: str = Field(default="")
    is_active: bool = Field(default=True)


class UpdateHospitalStatusRequest(BaseModel):
    is_active: bool


class ConfigurePolicyRequest(BaseModel):
    policy_code: str
    product_name: str
    default_sum_insured: Decimal
    auto_approval_threshold: Decimal
    buffer_percentage: Decimal = Field(default=Decimal("0.10"))
    auto_approved_diagnoses: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)


@router.post("/hospitals/onboard", status_code=status.HTTP_201_CREATED)
def onboard_hospital(
    payload: OnboardHospitalRequest,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_id: Optional[str] = Header("SYSTEM_ADMIN", alias="X-User-Id")
):
    verify_admin_role(x_user_role)
    service = NetworkAdminService(db)
    try:
        return service.onboard_hospital(
            hospital_id=payload.hospital_id,
            name=payload.name,
            city=payload.city,
            state=payload.state,
            tier=payload.tier,
            is_active=payload.is_active,
            actor_id=x_user_id or "SYSTEM_ADMIN"
        )
    except InvalidHospitalPayloadException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/hospitals/{hospital_id}/status")
def toggle_hospital_status(
    hospital_id: str,
    payload: UpdateHospitalStatusRequest,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_id: Optional[str] = Header("SYSTEM_ADMIN", alias="X-User-Id")
):
    verify_admin_role(x_user_role)
    service = NetworkAdminService(db)
    try:
        return service.toggle_hospital_status(
            hospital_id=hospital_id,
            is_active=payload.is_active,
            actor_id=x_user_id or "SYSTEM_ADMIN"
        )
    except InvalidHospitalPayloadException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/hospitals")
def list_network_hospitals(
    city: Optional[str] = None,
    tier: Optional[str] = None,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    service = NetworkAdminService(db)
    return service.get_hospitals_directory(city=city, tier=tier)


@router.post("/policies/configure")
def configure_policy_product(
    payload: ConfigurePolicyRequest,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_id: Optional[str] = Header("SYSTEM_ADMIN", alias="X-User-Id")
):
    verify_admin_role(x_user_role)
    service = NetworkAdminService(db)
    try:
        return service.configure_policy_product(
            policy_code=payload.policy_code,
            product_name=payload.product_name,
            default_sum_insured=payload.default_sum_insured,
            auto_approval_threshold=payload.auto_approval_threshold,
            buffer_percentage=payload.buffer_percentage,
            auto_approved_diagnoses=payload.auto_approved_diagnoses,
            exclusions=payload.exclusions,
            actor_id=x_user_id or "SYSTEM_ADMIN"
        )
    except InvalidPolicyConfigurationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/policies/{policy_code}")
def get_policy_configuration(
    policy_code: str,
    db: Session = Depends(get_db)
):
    service = NetworkAdminService(db)
    config = service.get_policy_product_config(policy_code)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy {policy_code} not found")
    return config
