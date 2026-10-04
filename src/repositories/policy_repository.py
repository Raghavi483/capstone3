"""
Repository Layer: Policy & Customer Data Access (AC-01)
Encapsulates database operations for customers and health insurance policies.
"""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import CustomerModel, PolicyModel


class PolicyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_customer_by_member_id(self, member_id: str) -> Optional[CustomerModel]:
        return self.db.query(CustomerModel).filter(CustomerModel.member_id == member_id).first()

    def create_customer(self, member_id: str, name: str, email: str, phone: str) -> CustomerModel:
        customer = CustomerModel(
            member_id=member_id,
            name=name,
            email=email,
            phone=phone
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_policy_by_id(self, policy_id: str) -> Optional[PolicyModel]:
        return self.db.query(PolicyModel).filter(PolicyModel.policy_id == policy_id).first()

    def get_policy_by_member_id(self, member_id: str) -> Optional[PolicyModel]:
        return self.db.query(PolicyModel).filter(PolicyModel.member_id == member_id).first()

    def create_policy(
        self,
        policy_id: str,
        member_id: str,
        product_name: str,
        sum_insured: Decimal,
        remaining_balance: Decimal,
        exclusions: List[str],
        is_active: bool = True
    ) -> PolicyModel:
        policy = PolicyModel(
            policy_id=policy_id,
            member_id=member_id,
            product_name=product_name,
            sum_insured=sum_insured,
            remaining_balance=remaining_balance,
            exclusions=exclusions,
            is_active=is_active
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
