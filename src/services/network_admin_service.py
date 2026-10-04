"""
Service: Network Hospital & Policy Administration Use Case Orchestrator.
Orchestrates domain validation, repository updates, and immutable audit logging.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.domain.network_admin_rule import (
    validate_hospital_onboarding,
    validate_policy_configuration,
    InvalidHospitalPayloadException,
    InvalidPolicyConfigurationException
)
from src.repositories.network_admin_repository import NetworkAdminRepository


class NetworkAdminService:
    def __init__(self, db: Session):
        self.repo = NetworkAdminRepository(db)

    def onboard_hospital(
        self,
        hospital_id: str,
        name: str,
        city: str,
        state: str,
        tier: str = "TIER_1",
        is_active: bool = True,
        actor_id: str = "SYSTEM_ADMIN"
    ) -> Dict[str, Any]:
        """Onboard a network hospital after domain validation and record audit."""
        validate_hospital_onboarding(
            hospital_id=hospital_id,
            name=name,
            tier=tier,
            city=city,
            state=state
        )
        record = self.repo.onboard_hospital(
            hospital_id=hospital_id,
            name=name,
            city=city,
            tier=tier,
            is_active=is_active
        )
        self.repo.log_audit(
            entity_type="HOSPITAL",
            entity_id=hospital_id,
            action="ONBOARD",
            actor_role="ADMIN",
            actor_id=actor_id,
            changes={"tier": tier, "city": city, "state": state, "is_active": is_active}
        )
        return record

    def toggle_hospital_status(
        self,
        hospital_id: str,
        is_active: bool,
        actor_id: str = "SYSTEM_ADMIN"
    ) -> Dict[str, Any]:
        """Update hospital active status and record audit."""
        result = self.repo.update_hospital_status(hospital_id=hospital_id, is_active=is_active)
        if not result:
            raise InvalidHospitalPayloadException(f"Hospital '{hospital_id}' not found")

        self.repo.log_audit(
            entity_type="HOSPITAL",
            entity_id=hospital_id,
            action="STATUS_TOGGLE",
            actor_role="ADMIN",
            actor_id=actor_id,
            changes={"is_active": is_active}
        )
        return result

    def get_hospitals_directory(
        self,
        city: Optional[str] = None,
        tier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query directory of network hospitals."""
        return self.repo.list_hospitals(city=city, tier=tier)

    def configure_policy_product(
        self,
        policy_code: str,
        product_name: str,
        default_sum_insured: Decimal,
        auto_approval_threshold: Decimal,
        buffer_percentage: Decimal,
        auto_approved_diagnoses: List[str],
        exclusions: List[str],
        actor_id: str = "SYSTEM_ADMIN"
    ) -> Dict[str, Any]:
        """Validate and configure policy product rules with audit."""
        validate_policy_configuration(
            policy_code=policy_code,
            product_name=product_name,
            default_sum_insured=default_sum_insured,
            auto_approval_threshold=auto_approval_threshold,
            buffer_percentage=buffer_percentage,
            auto_approved_diagnoses=auto_approved_diagnoses
        )
        result = self.repo.save_policy_config(
            policy_code=policy_code,
            product_name=product_name,
            default_sum_insured=default_sum_insured,
            auto_approval_threshold=auto_approval_threshold,
            buffer_percentage=buffer_percentage,
            auto_approved_diagnoses=auto_approved_diagnoses,
            exclusions=exclusions
        )
        self.repo.log_audit(
            entity_type="POLICY_CONFIG",
            entity_id=policy_code,
            action="CONFIGURE_POLICY",
            actor_role="ADMIN",
            actor_id=actor_id,
            changes={
                "auto_approval_threshold": str(auto_approval_threshold),
                "buffer_percentage": str(buffer_percentage),
                "auto_approved_diagnoses_count": len(auto_approved_diagnoses)
            }
        )
        return result

    def get_policy_product_config(self, policy_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve policy configuration."""
        return self.repo.get_policy_config(policy_code)
