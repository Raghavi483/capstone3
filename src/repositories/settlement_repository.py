"""
Repository Layer: Settlement Data Access (AC-07, NFR-02)
Encapsulates append-only database operations for claim settlements.
"""

from decimal import Decimal
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import SettlementModel


class SettlementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_settlement(
        self,
        settlement_id: str,
        claim_id: str,
        pre_auth_amount: Decimal,
        final_bill: Decimal,
        buffer_percentage: Decimal,
        bill_cap: Decimal,
        effective_bill: Decimal,
        deductible: Decimal,
        co_pay: Decimal,
        settlement_amount: Decimal,
        patient_responsibility: Decimal,
        status: str = "SETTLED"
    ) -> SettlementModel:
        settlement = SettlementModel(
            settlement_id=settlement_id,
            claim_id=claim_id,
            pre_auth_amount=pre_auth_amount,
            final_bill=final_bill,
            buffer_percentage=buffer_percentage,
            bill_cap=bill_cap,
            effective_bill=effective_bill,
            deductible=deductible,
            co_pay=co_pay,
            settlement_amount=settlement_amount,
            patient_responsibility=patient_responsibility,
            status=status
        )
        self.db.add(settlement)
        self.db.commit()
        self.db.refresh(settlement)
        return settlement

    def get_by_claim_id(self, claim_id: str) -> Optional[SettlementModel]:
        return (
            self.db.query(SettlementModel)
            .filter(SettlementModel.claim_id == claim_id)
            .order_by(SettlementModel.id.desc())
            .first()
        )

    def list_all(self) -> List[SettlementModel]:
        return self.db.query(SettlementModel).order_by(SettlementModel.id.desc()).all()
