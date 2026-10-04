"""
Controller Layer: Pre-Authorization & Admin Override Endpoints (AC-03, AC-04, AC-05, AC-10)
Exposes REST endpoints for hospital pre-auth submissions and elevated admin overrides.
"""

from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.repositories.database import get_db
from src.services.pre_auth_service import PreAuthService
from src.domain.adjudication_rule import UnauthorizedOverrideException

router = APIRouter(prefix="/api/v1", tags=["Pre-Authorization & Adjudication"])


class SubmitPreAuthRequest(BaseModel):
    member_id: str = Field(..., json_schema_extra={"example": "MEM-1001"})
    policy_id: str = Field(..., json_schema_extra={"example": "POL-5001"})
    hospital_id: str = Field(..., json_schema_extra={"example": "HOSP-001"})
    diagnosis: str = Field(..., json_schema_extra={"example": "ACUTE_APPENDICITIS"})
    estimated_cost: Decimal = Field(..., json_schema_extra={"example": "45000.00"})
    expected_admission_date: str = Field(..., json_schema_extra={"example": "2026-10-15"})


class AdminOverrideRequest(BaseModel):
    pre_auth_id: str = Field(..., json_schema_extra={"example": "PA-2002"})
    override_decision: str = Field(..., json_schema_extra={"example": "APPROVED"})
    override_amount: Decimal = Field(..., json_schema_extra={"example": "50000.00"})
    reason: str = Field(..., json_schema_extra={"example": "Exceptional clinical necessity approved by medical director"})
    actor_id: str = Field(..., json_schema_extra={"example": "admin_user_01"})


@router.post("/preauth/submit", status_code=status.HTTP_201_CREATED)
def submit_pre_auth(payload: SubmitPreAuthRequest, db: Session = Depends(get_db)):
    service = PreAuthService(db)
    result = service.submit_pre_auth(
        member_id=payload.member_id,
        policy_id=payload.policy_id,
        hospital_id=payload.hospital_id,
        diagnosis=payload.diagnosis,
        estimated_cost=payload.estimated_cost,
        expected_admission_date=payload.expected_admission_date
    )
    return result


@router.get("/preauth/{pre_auth_id}")
def get_pre_auth(pre_auth_id: str, db: Session = Depends(get_db)):
    service = PreAuthService(db)
    result = service.get_pre_auth_details(pre_auth_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pre-authorization not found")
    return result


@router.get("/preauth")
def list_pre_auths(db: Session = Depends(get_db)):
    service = PreAuthService(db)
    return service.list_all()


from src.controllers.auth_dependency import require_admin


@router.post("/admin/preauth/override")
def override_pre_auth(
    payload: AdminOverrideRequest,
    admin_id: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    service = PreAuthService(db)
    try:
        result = service.override_pre_auth(
            pre_auth_id=payload.pre_auth_id,
            override_decision=payload.override_decision,
            override_amount=payload.override_amount,
            reason=payload.reason,
            actor_role="ADMIN",
            actor_id=payload.actor_id or admin_id
        )
        return result
    except UnauthorizedOverrideException as ue:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ue))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
