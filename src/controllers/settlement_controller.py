"""
Controller Layer: Settlement API Endpoints (AC-07, NFR-01, NFR-02)
Exposes REST endpoints for claim settlement calculation, retrieval, and reporting.
"""

from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.repositories.database import get_db
from src.services.settlement_service import SettlementService
from src.domain.claim_state_rule import InvalidClaimStateException, SettledClaimImmutableException

router = APIRouter(prefix="/api/v1", tags=["Settlement Calculator"])


class ProcessSettlementRequest(BaseModel):
    deductible: Decimal = Field(default=Decimal("0.00"), json_schema_extra={"example": "1000.00"})
    co_pay: Decimal = Field(default=Decimal("0.00"), json_schema_extra={"example": "2000.00"})
    actor_id: str = Field(default="FINANCE_ADMIN", json_schema_extra={"example": "finance_officer_01"})


@router.post("/claims/{claim_id}/settle", status_code=status.HTTP_200_OK)
def settle_claim(claim_id: str, payload: ProcessSettlementRequest, db: Session = Depends(get_db)):
    service = SettlementService(db)
    try:
        return service.process_claim_settlement(
            claim_id=claim_id,
            deductible=payload.deductible,
            co_pay=payload.co_pay,
            actor_id=payload.actor_id
        )
    except InvalidClaimStateException as ie:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ie))
    except SettledClaimImmutableException as se:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(se))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/claims/{claim_id}/settlement")
def get_claim_settlement(claim_id: str, db: Session = Depends(get_db)):
    service = SettlementService(db)
    settlement = service.get_settlement_by_claim_id(claim_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found for this claim")
    return settlement


@router.get("/settlements")
def list_settlements(db: Session = Depends(get_db)):
    service = SettlementService(db)
    return service.list_all()
