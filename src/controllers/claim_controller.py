"""
Controller Layer: Claim Lifecycle, Admission & Timeline Endpoints (AC-06, AC-08, AC-09)
Exposes REST endpoints for admission tracking, final bill submission,
timeline inspection, and notification review.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.repositories.database import get_db
from src.services.admission_service import AdmissionService, BufferExceededException
from src.domain.claim_state_rule import InvalidClaimStateException, SettledClaimImmutableException

router = APIRouter(prefix="/api/v1", tags=["Claim Lifecycle & Admission"])


class AdmitPatientRequest(BaseModel):
    admission_date: str = Field(..., json_schema_extra={"example": "2026-10-15"})
    hospital_id: str = Field(..., json_schema_extra={"example": "HOSP-001"})


class ProcedureInput(BaseModel):
    procedure_code: str = Field(..., json_schema_extra={"example": "PR-APP-01"})
    description: str = Field(..., json_schema_extra={"example": "Appendectomy"})
    cost: Decimal = Field(..., json_schema_extra={"example": "42000.00"})


class DischargeAndBillRequest(BaseModel):
    discharge_date: str = Field(..., json_schema_extra={"example": "2026-10-18"})
    final_bill: Decimal = Field(..., json_schema_extra={"example": "48000.00"})
    hospital_id: str = Field(..., json_schema_extra={"example": "HOSP-001"})
    procedures: List[ProcedureInput] = Field(default_factory=list)


@router.post("/claims/{claim_id}/admit", status_code=status.HTTP_200_OK)
def admit_patient(claim_id: str, payload: AdmitPatientRequest, db: Session = Depends(get_db)):
    service = AdmissionService(db)
    try:
        return service.record_admission(
            claim_id=claim_id,
            admission_date=payload.admission_date,
            hospital_id=payload.hospital_id
        )
    except InvalidClaimStateException as ie:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ie))
    except SettledClaimImmutableException as se:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(se))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post("/claims/{claim_id}/discharge", status_code=status.HTTP_200_OK)
def discharge_patient(claim_id: str, payload: DischargeAndBillRequest, db: Session = Depends(get_db)):
    service = AdmissionService(db)
    try:
        procedures_dict = [p.model_dump() for p in payload.procedures]
        return service.submit_procedures_and_final_bill(
            claim_id=claim_id,
            procedures=procedures_dict,
            final_bill=payload.final_bill,
            discharge_date=payload.discharge_date,
            hospital_id=payload.hospital_id
        )
    except BufferExceededException as be:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(be))
    except InvalidClaimStateException as ie:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ie))
    except SettledClaimImmutableException as se:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(se))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/claims/{claim_id}/timeline")
def get_claim_timeline(claim_id: str, db: Session = Depends(get_db)):
    service = AdmissionService(db)
    return service.get_timeline(claim_id)


@router.get("/notifications/{recipient_id}")
def get_recipient_notifications(recipient_id: str, db: Session = Depends(get_db)):
    service = AdmissionService(db)
    return service.get_notifications(recipient_id)
