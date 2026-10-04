"""
Repository Layer: Pre-Authorization Data Access (AC-03, AC-04, AC-05, AC-10)
Encapsulates CRUD operations for pre-authorizations and append-only decision ledgers.
"""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import PreAuthModel, PreAuthDecisionModel, ClaimModel


class PreAuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_pre_auth(
        self,
        pre_auth_id: str,
        claim_id: str,
        member_id: str,
        policy_id: str,
        hospital_id: str,
        diagnosis: str,
        estimated_cost: Decimal,
        expected_admission_date: str,
        status: str = "PENDING",
        policy_version_tag: str = "v1.0.0"
    ) -> PreAuthModel:
        pre_auth = PreAuthModel(
            pre_auth_id=pre_auth_id,
            claim_id=claim_id,
            member_id=member_id,
            policy_id=policy_id,
            hospital_id=hospital_id,
            diagnosis=diagnosis,
            estimated_cost=estimated_cost,
            expected_admission_date=expected_admission_date,
            status=status,
            policy_version_tag=policy_version_tag
        )
        self.db.add(pre_auth)
        self.db.commit()
        self.db.refresh(pre_auth)
        return pre_auth

    def get_pre_auth(self, pre_auth_id: str) -> Optional[PreAuthModel]:
        return self.db.query(PreAuthModel).filter(PreAuthModel.pre_auth_id == pre_auth_id).first()

    def update_status(self, pre_auth_id: str, new_status: str) -> Optional[PreAuthModel]:
        pre_auth = self.get_pre_auth(pre_auth_id)
        if pre_auth:
            pre_auth.status = new_status
            self.db.commit()
            self.db.refresh(pre_auth)
        return pre_auth

    def add_decision(
        self,
        pre_auth_id: str,
        decision: str,
        approved_amount: Decimal,
        reason_codes: List[str],
        decider_type: str = "AUTO",
        decider_id: str = "SYSTEM"
    ) -> PreAuthDecisionModel:
        record = PreAuthDecisionModel(
            pre_auth_id=pre_auth_id,
            decision=decision,
            approved_amount=approved_amount,
            reason_codes=reason_codes,
            decider_type=decider_type,
            decider_id=decider_id
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_decisions(self, pre_auth_id: str) -> List[PreAuthDecisionModel]:
        return (
            self.db.query(PreAuthDecisionModel)
            .filter(PreAuthDecisionModel.pre_auth_id == pre_auth_id)
            .order_by(PreAuthDecisionModel.id.asc())
            .all()
        )

    def list_all(self) -> List[PreAuthModel]:
        return self.db.query(PreAuthModel).order_by(PreAuthModel.id.desc()).all()

    def list_pending(self) -> List[PreAuthModel]:
        return (
            self.db.query(PreAuthModel)
            .filter(PreAuthModel.status.in_(["PENDING", "QUERY_RAISED"]))
            .order_by(PreAuthModel.id.desc())
            .all()
        )
