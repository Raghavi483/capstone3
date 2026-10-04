"""
Repository: Network Hospital & Coverage Administration Persistence Layer.
Handles database access for hospital onboarding, tiering, policy configuration, and audit logging.
"""

from decimal import Decimal
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.models import (
    HospitalModel, NetworkHospitalModel, PolicyProductConfigModel, AuditEventModel
)


class NetworkAdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def onboard_hospital(
        self,
        hospital_id: str,
        name: str,
        city: str,
        tier: str = "TIER_1",
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Onboard a new hospital and create network mapping."""
        # Upsert / insert hospital
        hosp = self.db.query(HospitalModel).filter_by(hospital_id=hospital_id).first()
        if not hosp:
            hosp = HospitalModel(
                hospital_id=hospital_id,
                name=name,
                city=city,
                is_active=is_active
            )
            self.db.add(hosp)
            self.db.flush()
        else:
            hosp.name = name
            hosp.city = city
            hosp.is_active = is_active

        # Network hospital entry
        net_hosp = self.db.query(NetworkHospitalModel).filter_by(hospital_id=hospital_id).first()
        if not net_hosp:
            net_hosp = NetworkHospitalModel(
                hospital_id=hospital_id,
                tier=tier,
                is_in_network=is_active
            )
            self.db.add(net_hosp)
        else:
            net_hosp.tier = tier
            net_hosp.is_in_network = is_active

        self.db.commit()
        return {
            "hospital_id": hosp.hospital_id,
            "name": hosp.name,
            "city": hosp.city,
            "tier": net_hosp.tier,
            "is_active": hosp.is_active
        }

    def update_hospital_status(self, hospital_id: str, is_active: bool) -> Optional[Dict[str, Any]]:
        """Toggle hospital active / suspended status."""
        hosp = self.db.query(HospitalModel).filter_by(hospital_id=hospital_id).first()
        if not hosp:
            return None
        hosp.is_active = is_active

        net_hosp = self.db.query(NetworkHospitalModel).filter_by(hospital_id=hospital_id).first()
        if net_hosp:
            net_hosp.is_in_network = is_active

        self.db.commit()
        return {
            "hospital_id": hosp.hospital_id,
            "name": hosp.name,
            "city": hosp.city,
            "tier": net_hosp.tier if net_hosp else "TIER_1",
            "is_active": hosp.is_active
        }

    def list_hospitals(self, city: Optional[str] = None, tier: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query network hospital directory with optional city and tier filtering."""
        query = self.db.query(HospitalModel, NetworkHospitalModel).outerjoin(
            NetworkHospitalModel, HospitalModel.hospital_id == NetworkHospitalModel.hospital_id
        )
        if city:
            query = query.filter(HospitalModel.city.ilike(f"%{city}%"))
        if tier:
            query = query.filter(NetworkHospitalModel.tier == tier)

        results = query.all()
        output = []
        for hosp, net in results:
            output.append({
                "hospital_id": hosp.hospital_id,
                "name": hosp.name,
                "city": hosp.city,
                "tier": net.tier if net else "TIER_1",
                "is_active": hosp.is_active
            })
        return output

    def save_policy_config(
        self,
        policy_code: str,
        product_name: str,
        default_sum_insured: Decimal,
        auto_approval_threshold: Decimal,
        buffer_percentage: Decimal,
        auto_approved_diagnoses: List[str],
        exclusions: List[str]
    ) -> Dict[str, Any]:
        """Save or update policy product configuration."""
        config = self.db.query(PolicyProductConfigModel).filter_by(policy_code=policy_code).first()
        if not config:
            config = PolicyProductConfigModel(
                policy_code=policy_code,
                product_name=product_name,
                default_sum_insured=default_sum_insured,
                auto_approval_threshold=auto_approval_threshold,
                buffer_percentage=buffer_percentage,
                auto_approved_diagnoses=auto_approved_diagnoses,
                exclusions=exclusions
            )
            self.db.add(config)
        else:
            config.product_name = product_name
            config.default_sum_insured = default_sum_insured
            config.auto_approval_threshold = auto_approval_threshold
            config.buffer_percentage = buffer_percentage
            config.auto_approved_diagnoses = auto_approved_diagnoses
            config.exclusions = exclusions

        self.db.commit()
        return {
            "policy_code": config.policy_code,
            "product_name": config.product_name,
            "default_sum_insured": config.default_sum_insured,
            "auto_approval_threshold": config.auto_approval_threshold,
            "buffer_percentage": config.buffer_percentage,
            "auto_approved_diagnoses": config.auto_approved_diagnoses,
            "exclusions": config.exclusions
        }

    def get_policy_config(self, policy_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve policy product configuration."""
        config = self.db.query(PolicyProductConfigModel).filter_by(policy_code=policy_code).first()
        if not config:
            return None
        return {
            "policy_code": config.policy_code,
            "product_name": config.product_name,
            "default_sum_insured": config.default_sum_insured,
            "auto_approval_threshold": config.auto_approval_threshold,
            "buffer_percentage": config.buffer_percentage,
            "auto_approved_diagnoses": config.auto_approved_diagnoses,
            "exclusions": config.exclusions
        }

    def log_audit(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_role: str,
        actor_id: str,
        changes: Dict[str, Any]
    ) -> None:
        """Append an immutable audit entry."""
        audit = AuditEventModel(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_role=actor_role,
            actor_id=actor_id,
            changes_json=json.dumps(changes, default=str)
        )
        self.db.add(audit)
        self.db.commit()
