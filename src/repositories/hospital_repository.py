"""
Repository Layer: Hospital & Network Affiliation Data Access (AC-01, AC-02)
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from src.repositories.models import HospitalModel, NetworkHospitalModel


class HospitalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_hospital(self, hospital_id: str) -> Optional[HospitalModel]:
        return self.db.query(HospitalModel).filter(HospitalModel.hospital_id == hospital_id).first()

    def is_in_network(self, hospital_id: str) -> bool:
        net = (
            self.db.query(NetworkHospitalModel)
            .filter(
                NetworkHospitalModel.hospital_id == hospital_id,
                NetworkHospitalModel.is_in_network == True  # noqa: E712
            )
            .first()
        )
        return net is not None

    def list_network_hospitals(self) -> List[HospitalModel]:
        return (
            self.db.query(HospitalModel)
            .join(NetworkHospitalModel, HospitalModel.hospital_id == NetworkHospitalModel.hospital_id)
            .filter(
                HospitalModel.is_active == True,  # noqa: E712
                NetworkHospitalModel.is_in_network == True  # noqa: E712
            )
            .all()
        )

    def create_hospital(self, hospital_id: str, name: str, city: str, is_active: bool = True) -> HospitalModel:
        hospital = HospitalModel(
            hospital_id=hospital_id,
            name=name,
            city=city,
            is_active=is_active
        )
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital

    def link_network_hospital(self, hospital_id: str, tier: str = "TIER_1", is_in_network: bool = True) -> NetworkHospitalModel:
        link = NetworkHospitalModel(
            hospital_id=hospital_id,
            tier=tier,
            is_in_network=is_in_network
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link
