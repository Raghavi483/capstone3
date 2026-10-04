"""
Service Layer: Admission, Final Bill & Claim Lifecycle Service (AC-06, AC-08, AC-09)
Orchestrates patient admission, procedure tracking, final bill buffer checks,
strict state machine transitions, and notification dispatch.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.domain.admission_rule import (
    validate_final_bill_buffer,
    BillBufferValidationResult
)
from src.domain.claim_state_rule import (
    validate_claim_transition,
    InvalidClaimStateException,
    SettledClaimImmutableException
)
from src.domain.notification_rule import build_lifecycle_notification
from src.repositories.claim_repository import ClaimRepository
from src.repositories.pre_auth_repository import PreAuthRepository
from src.repositories.policy_repository import PolicyRepository


class BufferExceededException(Exception):
    """Raised when hospital final bill exceeds pre-auth amount + buffer cap."""
    pass


class AdmissionService:
    def __init__(self, db: Session):
        self.db = db
        self.claim_repo = ClaimRepository(db)
        self.pre_auth_repo = PreAuthRepository(db)
        self.policy_repo = PolicyRepository(db)

    def record_admission(
        self,
        claim_id: str,
        admission_date: str,
        hospital_id: str
    ) -> Dict[str, Any]:
        """AC-06 & AC-08: Records patient admission and transitions claim to ADMITTED."""
        claim = self.claim_repo.get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        # Verify Pre-Auth status is approved
        if claim.pre_auth_id:
            pre_auth = self.pre_auth_repo.get_pre_auth(claim.pre_auth_id)
            if not pre_auth or pre_auth.status not in {"APPROVED", "PARTIALLY_APPROVED"}:
                raise ValueError(
                    f"Cannot admit patient: pre-auth {claim.pre_auth_id} is in status {getattr(pre_auth, 'status', 'MISSING')}"
                )

        # Validate state machine transition (AC-08)
        new_state = validate_claim_transition(claim.status, "ADMITTED")

        # Update claim
        self.claim_repo.update_claim_status(claim_id, new_state)

        # Record admission details
        self.claim_repo.create_admission(claim_id, admission_date)

        # Timeline event (AC-09)
        self.claim_repo.add_timeline_event(
            claim_id=claim_id,
            event_type="ADMITTED",
            description=f"Patient admitted on {admission_date}",
            actor_role="HOSPITAL",
            actor_id=hospital_id
        )

        # Stubbed notifications (AC-09)
        notifications = build_lifecycle_notification(
            claim_id=claim_id,
            from_state="PRE_AUTH",
            to_state="ADMITTED",
            member_id=claim.member_id,
            hospital_id=hospital_id
        )
        for n in notifications:
            self.claim_repo.add_notification(
                recipient_type=n.recipient_type,
                recipient_id=n.recipient_id,
                message=n.message,
                channel=n.channel
            )

        return {
            "claim_id": claim_id,
            "status": new_state,
            "admission_date": admission_date,
            "hospital_id": hospital_id
        }

    def submit_procedures_and_final_bill(
        self,
        claim_id: str,
        procedures: List[Dict[str, Any]],
        final_bill: Decimal,
        discharge_date: str,
        hospital_id: str
    ) -> Dict[str, Any]:
        """AC-06 & AC-08: Submits bill with buffer check and transitions claim to DISCHARGED."""
        claim = self.claim_repo.get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        # Validate state machine (AC-08)
        new_state = validate_claim_transition(claim.status, "DISCHARGED")

        # Determine pre-auth approved amount
        pre_auth_amount = Decimal("0.00")
        if claim.pre_auth_id:
            decisions = self.pre_auth_repo.list_decisions(claim.pre_auth_id)
            if decisions:
                # Latest decision approved amount
                pre_auth_amount = decisions[-1].approved_amount

        # AC-06 Buffer Check (10% default buffer)
        buffer_result = validate_final_bill_buffer(
            pre_auth_amount=pre_auth_amount,
            final_bill=final_bill,
            buffer_percentage=Decimal("0.10")
        )

        if not buffer_result.is_valid:
            raise BufferExceededException(
                f"BILL_EXCEEDS_BUFFER_CAP: Final bill INR {final_bill} exceeds allowed cap INR {buffer_result.bill_cap}"
            )

        # Save procedures
        for p in procedures:
            self.claim_repo.add_procedure(
                claim_id=claim_id,
                procedure_name=p.get("description", p.get("procedure_name", "General Procedure")),
                procedure_code=p.get("procedure_code", "PROC-GEN"),
                cost=Decimal(str(p["cost"]))
            )

        # Save final bill in append-only table (AC-06)
        self.claim_repo.save_final_bill(
            claim_id=claim_id,
            total_bill_amount=final_bill,
            itemized_summary={"procedures": procedures, "bill_cap": str(buffer_result.bill_cap)}
        )

        # Update discharge date
        self.claim_repo.update_discharge_date(claim_id, discharge_date)

        # Update claim status to DISCHARGED
        self.claim_repo.update_claim_status(claim_id, new_state)

        # Record timeline event (AC-09)
        self.claim_repo.add_timeline_event(
            claim_id=claim_id,
            event_type="DISCHARGED",
            description=f"Discharged on {discharge_date}. Final bill INR {final_bill} within buffer cap INR {buffer_result.bill_cap}",
            actor_role="HOSPITAL",
            actor_id=hospital_id
        )

        # Notifications (AC-09)
        notifications = build_lifecycle_notification(
            claim_id=claim_id,
            from_state="ADMITTED",
            to_state="DISCHARGED",
            member_id=claim.member_id,
            hospital_id=hospital_id
        )
        for n in notifications:
            self.claim_repo.add_notification(
                recipient_type=n.recipient_type,
                recipient_id=n.recipient_id,
                message=n.message,
                channel=n.channel
            )

        return {
            "claim_id": claim_id,
            "status": new_state,
            "final_bill": str(final_bill),
            "pre_auth_amount": str(pre_auth_amount),
            "bill_cap": str(buffer_result.bill_cap),
            "effective_bill": str(buffer_result.effective_bill),
            "discharge_date": discharge_date
        }

    def get_timeline(self, claim_id: str) -> List[Dict[str, Any]]:
        """AC-09: Returns chronological timeline of claim events."""
        events = self.claim_repo.get_timeline(claim_id)
        return [
            {
                "id": e.id,
                "claim_id": e.claim_id,
                "event_type": e.event_type,
                "description": e.description,
                "actor_role": e.actor_role,
                "actor_id": e.actor_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None
            }
            for e in events
        ]

    def get_notifications(self, recipient_id: str) -> List[Dict[str, Any]]:
        """AC-09: Returns notifications for a member or hospital."""
        notifs = self.claim_repo.list_notifications(recipient_id)
        return [
            {
                "id": n.id,
                "recipient_type": n.recipient_type,
                "recipient_id": n.recipient_id,
                "channel": n.channel,
                "message": n.message,
                "timestamp": n.timestamp.isoformat() if n.timestamp else None
            }
            for n in notifs
        ]
