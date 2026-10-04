"""
Service Layer: Settlement Orchestration Service (AC-07, NFR-01, NFR-02)
Coordinates authoritative settlement calculation, policy balance updates,
claim immutability enforcement, and compliance audit trail emission.
"""

from decimal import Decimal
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from src.domain.settlement_rule import (
    SettlementCalculationInput,
    SettlementCalculationResult,
    calculate_settlement
)
from src.domain.claim_state_rule import (
    validate_claim_transition,
    InvalidClaimStateException,
    SettledClaimImmutableException
)
from src.domain.notification_rule import build_lifecycle_notification
from src.repositories.settlement_repository import SettlementRepository
from src.repositories.claim_repository import ClaimRepository
from src.repositories.pre_auth_repository import PreAuthRepository
from src.repositories.policy_repository import PolicyRepository
from src.repositories.models import AuditEventModel


class SettlementService:
    def __init__(self, db: Session):
        self.db = db
        self.settlement_repo = SettlementRepository(db)
        self.claim_repo = ClaimRepository(db)
        self.pre_auth_repo = PreAuthRepository(db)
        self.policy_repo = PolicyRepository(db)

    def process_claim_settlement(
        self,
        claim_id: str,
        deductible: Decimal = Decimal("0.00"),
        co_pay: Decimal = Decimal("0.00"),
        actor_id: str = "FINANCE_ADMIN"
    ) -> Dict[str, Any]:
        """AC-07: Processes invariant-checked settlement and finalizes claim."""
        claim = self.claim_repo.get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        # Validate state transition: DISCHARGED -> SETTLED (AC-08)
        new_state = validate_claim_transition(claim.status, "SETTLED")

        # Retrieve Final Bill
        final_bill_record = self.claim_repo.get_final_bill(claim_id)
        if not final_bill_record:
            raise ValueError(f"Final bill not found for claim {claim_id}")
        final_bill = final_bill_record.total_bill_amount

        # Retrieve Pre-Auth Amount
        pre_auth_amount = Decimal("0.00")
        if claim.pre_auth_id:
            decisions = self.pre_auth_repo.list_decisions(claim.pre_auth_id)
            if decisions:
                pre_auth_amount = decisions[-1].approved_amount

        # Retrieve Policy
        policy = self.policy_repo.get_policy_by_id(claim.policy_id)
        policy_balance = policy.remaining_balance if policy else None

        # Execute Domain Rule AC-07
        calc_input = SettlementCalculationInput(
            pre_auth_amount=pre_auth_amount,
            final_bill=final_bill,
            buffer_percentage=Decimal("0.10"),  # 10% default buffer
            deductible=deductible,
            co_pay=co_pay,
            policy_remaining_balance=policy_balance
        )
        calc_result: SettlementCalculationResult = calculate_settlement(calc_input)

        # Update Policy Remaining Balance
        if policy and calc_result.settlement_amount > Decimal("0.00"):
            policy.remaining_balance = max(
                Decimal("0.00"),
                policy.remaining_balance - calc_result.settlement_amount
            )

        # Persist Settlement in append-only table (AC-07)
        settlement_id = f"SET-{uuid.uuid4().hex[:8].upper()}"
        settlement_record = self.settlement_repo.create_settlement(
            settlement_id=settlement_id,
            claim_id=claim_id,
            pre_auth_amount=pre_auth_amount,
            final_bill=final_bill,
            buffer_percentage=calc_input.buffer_percentage,
            bill_cap=calc_result.bill_cap,
            effective_bill=calc_result.effective_bill,
            deductible=deductible,
            co_pay=co_pay,
            settlement_amount=calc_result.settlement_amount,
            patient_responsibility=calc_result.patient_responsibility,
            status="SETTLED"
        )

        # Update Claim Status to SETTLED and mark immutable (AC-08)
        self.claim_repo.update_claim_status(claim_id, "SETTLED", is_settled=True)

        # Append Timeline Event (AC-09)
        self.claim_repo.add_timeline_event(
            claim_id=claim_id,
            event_type="SETTLED",
            description=(
                f"Settlement finalized: Insurer Payout INR {calc_result.settlement_amount}, "
                f"Patient Responsibility INR {calc_result.patient_responsibility}."
            ),
            actor_role="INSURER_FINANCE",
            actor_id=actor_id
        )

        # Append-Only Audit Trail (NFR-02)
        audit_event = AuditEventModel(
            entity_type="CLAIM_SETTLEMENT",
            entity_id=settlement_id,
            action="SETTLEMENT_FINALIZED",
            actor_role="INSURER_FINANCE",
            actor_id=actor_id,
            changes_json=(
                f'{{"claim_id": "{claim_id}", "settlement_amount": "{calc_result.settlement_amount}", '
                f'"patient_responsibility": "{calc_result.patient_responsibility}"}}'
            )
        )
        self.db.add(audit_event)

        # Dispatch Stubbed Notifications (AC-09)
        notifications = build_lifecycle_notification(
            claim_id=claim_id,
            from_state="DISCHARGED",
            to_state="SETTLED",
            member_id=claim.member_id,
            hospital_id=claim.hospital_id
        )
        for n in notifications:
            self.claim_repo.add_notification(
                recipient_type=n.recipient_type,
                recipient_id=n.recipient_id,
                message=n.message,
                channel=n.channel
            )

        self.db.commit()

        return {
            "settlement_id": settlement_id,
            "claim_id": claim_id,
            "final_bill": str(final_bill),
            "pre_auth_amount": str(pre_auth_amount),
            "buffer_amount": str(calc_result.buffer_amount),
            "bill_cap": str(calc_result.bill_cap),
            "effective_bill": str(calc_result.effective_bill),
            "deductible": str(deductible),
            "co_pay": str(co_pay),
            "settlement_amount": str(calc_result.settlement_amount),
            "patient_responsibility": str(calc_result.patient_responsibility),
            "status": "SETTLED"
        }

    def get_settlement_by_claim_id(self, claim_id: str) -> Optional[Dict[str, Any]]:
        s = self.settlement_repo.get_by_claim_id(claim_id)
        if not s:
            return None
        return {
            "settlement_id": s.settlement_id,
            "claim_id": s.claim_id,
            "pre_auth_amount": str(s.pre_auth_amount),
            "final_bill": str(s.final_bill),
            "buffer_percentage": str(s.buffer_percentage),
            "bill_cap": str(s.bill_cap),
            "effective_bill": str(s.effective_bill),
            "deductible": str(s.deductible),
            "co_pay": str(s.co_pay),
            "settlement_amount": str(s.settlement_amount),
            "patient_responsibility": str(s.patient_responsibility),
            "status": s.status,
            "settled_at": s.settled_at.isoformat() if s.settled_at else None
        }

    def list_all(self) -> List[Dict[str, Any]]:
        items = self.settlement_repo.list_all()
        return [
            {
                "settlement_id": s.settlement_id,
                "claim_id": s.claim_id,
                "final_bill": str(s.final_bill),
                "settlement_amount": str(s.settlement_amount),
                "patient_responsibility": str(s.patient_responsibility),
                "status": s.status,
                "settled_at": s.settled_at.isoformat() if s.settled_at else None
            }
            for s in items
        ]
