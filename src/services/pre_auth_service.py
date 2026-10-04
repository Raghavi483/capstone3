"""
Service Layer: Pre-Authorization & Adjudication Service (AC-03, AC-04, AC-05, AC-10)
Orchestrates pre-auth submissions, rule auto-approval engine,
append-only decision ledgers, and elevated admin overrides.
"""

from decimal import Decimal
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from src.domain.pre_auth_rule import (
    PreAuthSubmissionInput,
    create_pre_auth_submission,
    AutoApprovalEngineConfig,
    evaluate_auto_approval,
    transition_pre_auth_decision
)
from src.domain.adjudication_rule import (
    AdminOverrideInput,
    evaluate_admin_override
)
from src.repositories.pre_auth_repository import PreAuthRepository
from src.repositories.policy_repository import PolicyRepository
from src.repositories.hospital_repository import HospitalRepository
from src.repositories.models import ClaimModel, ClaimTimelineEventModel, AuditEventModel, PolicyRuleVersionModel
from src.utils.logger import get_logger

logger = get_logger("medicard.preauth")


class PreAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.pre_auth_repo = PreAuthRepository(db)
        self.policy_repo = PolicyRepository(db)
        self.hospital_repo = HospitalRepository(db)

    def submit_pre_auth(
        self,
        member_id: str,
        policy_id: str,
        hospital_id: str,
        diagnosis: str,
        estimated_cost: Decimal,
        expected_admission_date: str
    ) -> Dict[str, Any]:
        """AC-03 & AC-05: Submits pre-auth, evaluates auto-approval, and creates claim entity."""
        submission_input = PreAuthSubmissionInput(
            member_id=member_id,
            policy_id=policy_id,
            hospital_id=hospital_id,
            diagnosis=diagnosis,
            estimated_cost=estimated_cost,
            expected_admission_date=expected_admission_date
        )
        pre_auth_entity = create_pre_auth_submission(submission_input)

        # Retrieve policy for exclusions and remaining balance
        policy = self.policy_repo.get_policy_by_id(policy_id)
        exclusions = policy.exclusions if policy else []
        remaining_balance = policy.remaining_balance if policy else Decimal("0.00")

        # Retrieve active PolicyRuleVersion (Priority 3B / NET-02)
        rule_version = self.db.query(PolicyRuleVersionModel).filter_by(
            policy_code=policy_id, is_active=True
        ).order_by(PolicyRuleVersionModel.id.desc()).first()

        if rule_version:
            policy_version_tag = rule_version.version_tag
            threshold = rule_version.auto_approval_threshold
            auto_diagnoses = rule_version.auto_approved_diagnoses
            if rule_version.exclusions:
                exclusions = rule_version.exclusions
        else:
            policy_version_tag = "v1.0.0"
            threshold = Decimal("50000.00")
            auto_diagnoses = [
                "ACUTE_APPENDICITIS", "CATARACT_SURGERY", "NORMAL_DELIVERY", "HERNIA_REPAIR"
            ]

        # Evaluate auto-approval rules (AC-05)
        config = AutoApprovalEngineConfig(
            cost_threshold=threshold,
            auto_approved_diagnoses=auto_diagnoses,
            exclusions=exclusions
        )
        auto_result = evaluate_auto_approval(
            diagnosis=diagnosis,
            estimated_cost=estimated_cost,
            remaining_balance=remaining_balance,
            config=config
        )

        # Set entity status from auto-decision
        pre_auth_entity.status = auto_result.decision

        # Persist Pre-Auth
        pre_auth_record = self.pre_auth_repo.create_pre_auth(
            pre_auth_id=pre_auth_entity.pre_auth_id,
            claim_id=pre_auth_entity.claim_id,
            member_id=pre_auth_entity.member_id,
            policy_id=pre_auth_entity.policy_id,
            hospital_id=pre_auth_entity.hospital_id,
            diagnosis=pre_auth_entity.diagnosis,
            estimated_cost=pre_auth_entity.estimated_cost,
            expected_admission_date=pre_auth_entity.expected_admission_date,
            status=pre_auth_entity.status,
            policy_version_tag=policy_version_tag
        )

        # Persist Decision in append-only table (AC-04)
        decision_record = self.pre_auth_repo.add_decision(
            pre_auth_id=pre_auth_record.pre_auth_id,
            decision=auto_result.decision,
            approved_amount=auto_result.approved_amount,
            reason_codes=auto_result.reason_codes,
            decider_type="AUTO",
            decider_id="SYSTEM"
        )

        # Create Claim record bound to the historical policy version tag
        claim = ClaimModel(
            claim_id=pre_auth_entity.claim_id,
            member_id=member_id,
            policy_id=policy_id,
            hospital_id=hospital_id,
            pre_auth_id=pre_auth_entity.pre_auth_id,
            status="PRE_AUTH",
            policy_version_tag=policy_version_tag
        )
        self.db.add(claim)

        # Record timeline events (AC-09)
        te_submit = ClaimTimelineEventModel(
            claim_id=pre_auth_entity.claim_id,
            event_type="PRE_AUTH_SUBMITTED",
            description=f"Pre-authorization requested for amount INR {estimated_cost}",
            actor_role="HOSPITAL",
            actor_id=hospital_id
        )
        te_decide = ClaimTimelineEventModel(
            claim_id=pre_auth_entity.claim_id,
            event_type=f"PRE_AUTH_{auto_result.decision}",
            description=f"Pre-authorization evaluated: {auto_result.decision} (Reasons: {', '.join(auto_result.reason_codes)})",
            actor_role="SYSTEM",
            actor_id="RULES_ENGINE"
        )
        self.db.add_all([te_submit, te_decide])
        self.db.commit()

        return {
            "pre_auth_id": pre_auth_record.pre_auth_id,
            "claim_id": pre_auth_record.claim_id,
            "status": pre_auth_record.status,
            "estimated_cost": str(pre_auth_record.estimated_cost),
            "approved_amount": str(decision_record.approved_amount),
            "reason_codes": decision_record.reason_codes,
            "expected_admission_date": pre_auth_record.expected_admission_date
        }

    def override_pre_auth(
        self,
        pre_auth_id: str,
        override_decision: str,
        override_amount: Decimal,
        reason: str,
        actor_role: str,
        actor_id: str
    ) -> Dict[str, Any]:
        """AC-10: Executes elevated insurer administrator override."""
        pre_auth = self.pre_auth_repo.get_pre_auth(pre_auth_id)
        if not pre_auth:
            raise ValueError(f"Pre-authorization {pre_auth_id} not found")

        policy = self.policy_repo.get_policy_by_id(pre_auth.policy_id)
        policy_balance = policy.remaining_balance if policy else Decimal("0.00")

        override_input = AdminOverrideInput(
            pre_auth_id=pre_auth_id,
            current_status=pre_auth.status,
            override_decision=override_decision,
            override_amount=override_amount,
            policy_balance=policy_balance,
            reason=reason,
            actor_role=actor_role,
            actor_id=actor_id
        )
        override_result = evaluate_admin_override(override_input)

        # Update status
        self.pre_auth_repo.update_status(pre_auth_id, override_result.new_status)

        # Record override in append-only decision ledger (AC-04)
        decision_record = self.pre_auth_repo.add_decision(
            pre_auth_id=pre_auth_id,
            decision=override_result.new_status,
            approved_amount=override_result.authorized_amount,
            reason_codes=override_result.reason_codes,
            decider_type="OVERRIDE",
            decider_id=actor_id
        )

        # Immutable Audit Event (NFR-02)
        audit_event = AuditEventModel(
            entity_type="PRE_AUTH_OVERRIDE",
            entity_id=pre_auth_id,
            action="ADMIN_OVERRIDE",
            actor_role=actor_role,
            actor_id=actor_id,
            changes_json=str(override_result.audit_payload)
        )
        self.db.add(audit_event)

        # Timeline Event
        te = ClaimTimelineEventModel(
            claim_id=pre_auth.claim_id,
            event_type="PRE_AUTH_OVERRIDDEN",
            description=f"Admin {actor_id} overrode pre-auth to {override_result.new_status} (Amount: INR {override_amount}). Justification: {reason}",
            actor_role="ADMIN",
            actor_id=actor_id
        )
        self.db.add(te)
        self.db.commit()

        return {
            "pre_auth_id": pre_auth_id,
            "status": override_result.new_status,
            "approved_amount": str(override_result.authorized_amount),
            "is_override": True,
            "actor_id": actor_id,
            "reason": reason
        }

    def get_pre_auth_details(self, pre_auth_id: str) -> Optional[Dict[str, Any]]:
        pre_auth = self.pre_auth_repo.get_pre_auth(pre_auth_id)
        if not pre_auth:
            return None
        decisions = self.pre_auth_repo.list_decisions(pre_auth_id)
        return {
            "pre_auth_id": pre_auth.pre_auth_id,
            "claim_id": pre_auth.claim_id,
            "member_id": pre_auth.member_id,
            "policy_id": pre_auth.policy_id,
            "hospital_id": pre_auth.hospital_id,
            "estimated_cost": str(pre_auth.estimated_cost),
            "expected_admission_date": pre_auth.expected_admission_date,
            "status": pre_auth.status,
            "decisions": [
                {
                    "decision": d.decision,
                    "approved_amount": str(d.approved_amount),
                    "reason_codes": d.reason_codes,
                    "decider_type": d.decider_type,
                    "decider_id": d.decider_id,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in decisions
            ]
        }

    def list_all(self) -> List[Dict[str, Any]]:
        items = self.pre_auth_repo.list_all()
        return [
            {
                "pre_auth_id": p.pre_auth_id,
                "claim_id": p.claim_id,
                "member_id": p.member_id,
                "policy_id": p.policy_id,
                "hospital_id": p.hospital_id,
                "estimated_cost": str(p.estimated_cost),
                "expected_admission_date": p.expected_admission_date,
                "status": p.status
            }
            for p in items
        ]
