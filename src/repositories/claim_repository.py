"""
Repository Layer: Claim & Admission Data Access (AC-06, AC-08, AC-09)
Encapsulates CRUD for claims, admissions, procedure records, final bills,
timeline events, and stubbed notifications.
"""

from decimal import Decimal
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.models import (
    ClaimModel, AdmissionModel, ProcedureRecordModel,
    FinalBillModel, ClaimTimelineEventModel, NotificationModel
)


class ClaimRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_claim(self, claim_id: str) -> Optional[ClaimModel]:
        return self.db.query(ClaimModel).filter(ClaimModel.claim_id == claim_id).first()

    def update_claim_status(self, claim_id: str, new_status: str, is_settled: bool = False) -> Optional[ClaimModel]:
        claim = self.get_claim(claim_id)
        if claim:
            claim.status = new_status
            if is_settled:
                claim.is_settled = True
            self.db.commit()
            self.db.refresh(claim)
        return claim

    def create_admission(self, claim_id: str, admission_date: str) -> AdmissionModel:
        admission = AdmissionModel(
            claim_id=claim_id,
            admission_date=admission_date
        )
        self.db.add(admission)
        self.db.commit()
        self.db.refresh(admission)
        return admission

    def get_admission(self, claim_id: str) -> Optional[AdmissionModel]:
        return self.db.query(AdmissionModel).filter(AdmissionModel.claim_id == claim_id).first()

    def update_discharge_date(self, claim_id: str, discharge_date: str) -> Optional[AdmissionModel]:
        adm = self.get_admission(claim_id)
        if adm:
            adm.discharge_date = discharge_date
            self.db.commit()
            self.db.refresh(adm)
        return adm

    def add_procedure(
        self,
        claim_id: str,
        procedure_name: str,
        procedure_code: str,
        cost: Decimal
    ) -> ProcedureRecordModel:
        proc = ProcedureRecordModel(
            claim_id=claim_id,
            procedure_name=procedure_name,
            procedure_code=procedure_code,
            cost=cost
        )
        self.db.add(proc)
        self.db.commit()
        self.db.refresh(proc)
        return proc

    def list_procedures(self, claim_id: str) -> List[ProcedureRecordModel]:
        return self.db.query(ProcedureRecordModel).filter(ProcedureRecordModel.claim_id == claim_id).all()

    def save_final_bill(
        self,
        claim_id: str,
        total_bill_amount: Decimal,
        itemized_summary: Dict[str, Any]
    ) -> FinalBillModel:
        bill = FinalBillModel(
            claim_id=claim_id,
            total_bill_amount=total_bill_amount,
            itemized_summary_json=json.dumps(itemized_summary or {}, default=str)
        )
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)
        return bill

    def get_final_bill(self, claim_id: str) -> Optional[FinalBillModel]:
        return (
            self.db.query(FinalBillModel)
            .filter(FinalBillModel.claim_id == claim_id)
            .order_by(FinalBillModel.id.desc())
            .first()
        )

    def add_timeline_event(
        self,
        claim_id: str,
        event_type: str,
        description: str,
        actor_role: str,
        actor_id: str
    ) -> ClaimTimelineEventModel:
        te = ClaimTimelineEventModel(
            claim_id=claim_id,
            event_type=event_type,
            description=description,
            actor_role=actor_role,
            actor_id=actor_id
        )
        self.db.add(te)
        self.db.commit()
        self.db.refresh(te)
        return te

    def get_timeline(self, claim_id: str) -> List[ClaimTimelineEventModel]:
        return (
            self.db.query(ClaimTimelineEventModel)
            .filter(ClaimTimelineEventModel.claim_id == claim_id)
            .order_by(ClaimTimelineEventModel.id.asc())
            .all()
        )

    def add_notification(
        self,
        recipient_type: str,
        recipient_id: str,
        message: str,
        channel: str = "IN_APP"
    ) -> NotificationModel:
        notif = NotificationModel(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            message=message,
            channel=channel
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def list_notifications(self, recipient_id: str) -> List[NotificationModel]:
        return (
            self.db.query(NotificationModel)
            .filter(NotificationModel.recipient_id == recipient_id)
            .order_by(NotificationModel.id.desc())
            .all()
        )
