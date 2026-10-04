"""
Service Layer: Eligibility & Policy Orchestration (AC-01, AC-02)
Coordinates customer registration, policy linkage, coverage querying,
and hospital eligibility checks while recording audit records.
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.domain.eligibility_rule import (
    CustomerPolicyCoverage,
    EligibilityCheckInput,
    EligibilityEvaluationResult,
    evaluate_member_eligibility
)
from src.repositories.policy_repository import PolicyRepository
from src.repositories.hospital_repository import HospitalRepository
from src.repositories.models import AuditEventModel


class EligibilityService:
    def __init__(self, db: Session):
        self.db = db
        self.policy_repo = PolicyRepository(db)
        self.hospital_repo = HospitalRepository(db)

    def register_customer_and_policy(
        self,
        member_id: str,
        name: str,
        email: str,
        phone: str,
        policy_id: str,
        product_name: str,
        sum_insured: Decimal,
        exclusions: List[str]
    ) -> Dict[str, Any]:
        """AC-01: Registers a customer and establishes policy linkage."""
        customer = self.policy_repo.get_customer_by_member_id(member_id)
        if not customer:
            customer = self.policy_repo.create_customer(member_id, name, email, phone)

        policy = self.policy_repo.get_policy_by_id(policy_id)
        if not policy:
            policy = self.policy_repo.create_policy(
                policy_id=policy_id,
                member_id=member_id,
                product_name=product_name,
                sum_insured=sum_insured,
                remaining_balance=sum_insured,
                exclusions=exclusions,
                is_active=True
            )

        network_hospitals = [h.hospital_id for h in self.hospital_repo.list_network_hospitals()]
        coverage = CustomerPolicyCoverage(
            member_id=customer.member_id,
            policy_id=policy.policy_id,
            product_name=policy.product_name,
            sum_insured=policy.sum_insured,
            remaining_balance=policy.remaining_balance,
            exclusions=policy.exclusions,
            network_hospitals=network_hospitals,
            is_active=policy.is_active
        )
        return {
            "customer": {
                "member_id": customer.member_id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone
            },
            "coverage": coverage
        }

    def get_coverage(self, member_id: str, policy_id: str) -> Optional[CustomerPolicyCoverage]:
        """AC-01: Retrieves coverage details for a customer policy."""
        policy = self.policy_repo.get_policy_by_id(policy_id)
        if not policy or policy.member_id != member_id:
            return None

        network_hospitals = [h.hospital_id for h in self.hospital_repo.list_network_hospitals()]
        return CustomerPolicyCoverage(
            member_id=policy.member_id,
            policy_id=policy.policy_id,
            product_name=policy.product_name,
            sum_insured=policy.sum_insured,
            remaining_balance=policy.remaining_balance,
            exclusions=policy.exclusions,
            network_hospitals=network_hospitals,
            is_active=policy.is_active
        )

    def get_first_policy_coverage_for_member(self, member_id: str) -> Optional[CustomerPolicyCoverage]:
        """Retrieves first active coverage for a member."""
        policy = self.policy_repo.get_policy_by_member_id(member_id)
        if not policy:
            return None
        return self.get_coverage(member_id=member_id, policy_id=policy.policy_id)

    def check_eligibility(
        self,
        member_id: str,
        policy_id: str,
        hospital_id: str
    ) -> EligibilityEvaluationResult:
        """AC-02: Adjudicates hospital eligibility lookup and records audit event."""
        policy = self.policy_repo.get_policy_by_id(policy_id)
        is_hospital_in_network = self.hospital_repo.is_in_network(hospital_id)

        if not policy or policy.member_id != member_id:
            result = EligibilityEvaluationResult(
                status="NOT_ELIGIBLE",
                is_eligible=False,
                reason_codes=["POL_NOT_FOUND"],
                available_balance=Decimal("0.00")
            )
        else:
            check_input = EligibilityCheckInput(
                member_id=member_id,
                policy_id=policy_id,
                hospital_id=hospital_id,
                is_policy_active=policy.is_active,
                is_hospital_in_network=is_hospital_in_network,
                remaining_balance=policy.remaining_balance
            )
            result = evaluate_member_eligibility(check_input)

        # Audit recording (NFR-02)
        audit_entry = AuditEventModel(
            entity_type="ELIGIBILITY",
            entity_id=f"{member_id}:{policy_id}",
            action="ELIGIBILITY_LOOKUP",
            actor_role="HOSPITAL",
            actor_id=hospital_id,
            changes_json=f'{{"status": "{result.status}", "reasons": {result.reason_codes}}}'
        )
        self.db.add(audit_entry)
        self.db.commit()

        return result
