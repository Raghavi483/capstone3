"""
Domain Layer: Network Hospital Rules
Enforces rules governing network hospital affiliations and tier validations.
"""

from typing import List


class NetworkHospitalRule:
    """Evaluates whether a hospital belongs to the authorized cashless network."""

    @staticmethod
    def is_hospital_in_network(hospital_id: str, network_hospital_ids: List[str]) -> bool:
        if not hospital_id or not network_hospital_ids:
            return False
        return hospital_id.strip() in [h.strip() for h in network_hospital_ids]
