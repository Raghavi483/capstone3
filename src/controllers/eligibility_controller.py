"""
Controller Layer: Eligibility & Policy API Endpoints (AC-01, AC-02)
Exposes REST endpoints for registration, coverage view, and eligibility check.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.repositories.database import get_db
from src.services.eligibility_service import EligibilityService

router = APIRouter(prefix="/api/v1", tags=["Eligibility & Coverage"])


class RegisterCustomerRequest(BaseModel):
    member_id: str = Field(..., json_schema_extra={"example": "MEM-1001"})
    name: str = Field(..., json_schema_extra={"example": "John Doe"})
    email: str = Field(..., json_schema_extra={"example": "john@example.com"})
    phone: str = Field(..., json_schema_extra={"example": "+1-555-0100"})
    policy_id: str = Field(..., json_schema_extra={"example": "POL-5001"})
    product_name: str = Field(..., json_schema_extra={"example": "MediCard Gold"})
    sum_insured: Decimal = Field(..., json_schema_extra={"example": "500000.00"})
    exclusions: List[str] = Field(default_factory=list, json_schema_extra={"example": ["COSMETIC_SURGERY"]})


class EligibilityCheckRequest(BaseModel):
    member_id: str = Field(..., json_schema_extra={"example": "MEM-1001"})
    policy_id: str = Field(..., json_schema_extra={"example": "POL-5001"})
    hospital_id: str = Field(..., json_schema_extra={"example": "HOSP-001"})


@router.post("/customers/register", status_code=status.HTTP_201_CREATED)
def register_customer(payload: RegisterCustomerRequest, db: Session = Depends(get_db)):
    service = EligibilityService(db)
    result = service.register_customer_and_policy(
        member_id=payload.member_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        policy_id=payload.policy_id,
        product_name=payload.product_name,
        sum_insured=payload.sum_insured,
        exclusions=payload.exclusions
    )
    cov = result["coverage"]
    return {
        "customer": result["customer"],
        "coverage": {
            "member_id": cov.member_id,
            "policy_id": cov.policy_id,
            "product_name": cov.product_name,
            "sum_insured": str(cov.sum_insured),
            "remaining_balance": str(cov.remaining_balance),
            "exclusions": cov.exclusions,
            "network_hospitals": cov.network_hospitals,
            "is_active": cov.is_active
        }
    }


from src.controllers.auth_dependency import verify_customer_tenancy


@router.get("/customers/{member_id}/coverage")
def get_customer_all_coverage(
    member_id: str,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_member_id: Optional[str] = Header(None, alias="X-Member-Id"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    verify_customer_tenancy(member_id, x_user_role, x_member_id, x_user_id)
    service = EligibilityService(db)
    coverage = service.get_first_policy_coverage_for_member(member_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Customer policy not found")
    return {
        "member_id": coverage.member_id,
        "policy_id": coverage.policy_id,
        "product_name": coverage.product_name,
        "sum_insured": str(coverage.sum_insured),
        "remaining_balance": str(coverage.remaining_balance),
        "exclusions": coverage.exclusions,
        "network_hospitals": coverage.network_hospitals,
        "is_active": coverage.is_active
    }


@router.get("/customers/{member_id}/policies/{policy_id}/coverage")
def get_policy_coverage(
    member_id: str,
    policy_id: str,
    db: Session = Depends(get_db),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_member_id: Optional[str] = Header(None, alias="X-Member-Id"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    verify_customer_tenancy(member_id, x_user_role, x_member_id, x_user_id)
    service = EligibilityService(db)
    coverage = service.get_coverage(member_id=member_id, policy_id=policy_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Policy or customer not found")
    return {
        "member_id": coverage.member_id,
        "policy_id": coverage.policy_id,
        "product_name": coverage.product_name,
        "sum_insured": str(coverage.sum_insured),
        "remaining_balance": str(coverage.remaining_balance),
        "exclusions": coverage.exclusions,
        "network_hospitals": coverage.network_hospitals,
        "is_active": coverage.is_active
    }


@router.post("/eligibility/check")
def check_hospital_eligibility(payload: EligibilityCheckRequest, db: Session = Depends(get_db)):
    service = EligibilityService(db)
    result = service.check_eligibility(
        member_id=payload.member_id,
        policy_id=payload.policy_id,
        hospital_id=payload.hospital_id
    )
    return {
        "status": result.status,
        "is_eligible": result.is_eligible,
        "reason_codes": result.reason_codes,
        "available_balance": str(result.available_balance)
    }
