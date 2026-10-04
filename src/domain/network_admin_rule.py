"""
Domain Rules: Network Hospital & Coverage Administration (specs/network_admin_spec.md).
Enforces:
- Rule NET-01 (Active Status Gate): Only hospitals with active_status == True are eligible.
- Rule NET-02 (Policy Rule Immutability & Validation): Positive threshold, valid tiers, non-negative monetary caps.
"""

from decimal import Decimal
from typing import List, Optional


class InvalidHospitalPayloadException(Exception):
    """Raised when hospital payload fails validation."""
    pass


class InvalidPolicyConfigurationException(Exception):
    """Raised when policy configuration fails validation."""
    pass


VALID_TIERS = {"TIER_1", "TIER_2", "TIER_3"}


def validate_hospital_onboarding(
    hospital_id: str,
    name: str,
    tier: str,
    city: str,
    state: str
) -> None:
    """Validate hospital onboarding fields."""
    if not hospital_id or not hospital_id.strip():
        raise InvalidHospitalPayloadException("hospital_id cannot be empty")
    if not name or not name.strip():
        raise InvalidHospitalPayloadException("hospital name cannot be empty")
    if tier not in VALID_TIERS:
        raise InvalidHospitalPayloadException(f"Invalid tier '{tier}'. Must be one of {sorted(VALID_TIERS)}")
    if not city or not city.strip():
        raise InvalidHospitalPayloadException("city cannot be empty")
    if not state or not state.strip():
        raise InvalidHospitalPayloadException("state cannot be empty")


def validate_policy_configuration(
    policy_code: str,
    product_name: str,
    default_sum_insured: Decimal,
    auto_approval_threshold: Decimal,
    buffer_percentage: Decimal,
    auto_approved_diagnoses: List[str]
) -> None:
    """Validate policy product parameters."""
    if not policy_code or not policy_code.strip():
        raise InvalidPolicyConfigurationException("policy_code cannot be empty")
    if not product_name or not product_name.strip():
        raise InvalidPolicyConfigurationException("product_name cannot be empty")
    if default_sum_insured <= Decimal("0.00"):
        raise InvalidPolicyConfigurationException("default_sum_insured must be strictly positive")
    if auto_approval_threshold < Decimal("0.00"):
        raise InvalidPolicyConfigurationException("Threshold must be non-negative")
    if buffer_percentage < Decimal("0.00") or buffer_percentage > Decimal("1.00"):
        raise InvalidPolicyConfigurationException("buffer_percentage must be between 0.00 and 1.00")
    if not isinstance(auto_approved_diagnoses, list):
        raise InvalidPolicyConfigurationException("auto_approved_diagnoses must be a list")
