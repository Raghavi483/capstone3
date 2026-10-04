"""
SQLAlchemy ORM Models for MediCard Platform.
Enforces Decimal representation for all currency amounts and structured entities.
"""

from datetime import datetime, timezone
from decimal import Decimal
import json
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey
)
from src.repositories.database import Base


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PolicyModel(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String(50), unique=True, index=True, nullable=False)
    member_id = Column(String(50), ForeignKey("customers.member_id"), index=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    sum_insured = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    remaining_balance = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    exclusions_json = Column(Text, default="[]", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def exclusions(self):
        return json.loads(self.exclusions_json or "[]")

    @exclusions.setter
    def exclusions(self, value):
        self.exclusions_json = json.dumps(value or [])


class HospitalModel(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NetworkHospitalModel(Base):
    __tablename__ = "network_hospitals"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(String(50), ForeignKey("hospitals.hospital_id"), index=True, nullable=False)
    tier = Column(String(20), default="TIER_1", nullable=False)
    is_in_network = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PreAuthModel(Base):
    __tablename__ = "pre_authorizations"

    id = Column(Integer, primary_key=True, index=True)
    pre_auth_id = Column(String(50), unique=True, index=True, nullable=False)
    claim_id = Column(String(50), index=True, nullable=False)
    hospital_id = Column(String(50), nullable=False)
    member_id = Column(String(50), nullable=False)
    policy_id = Column(String(50), nullable=False)
    diagnosis = Column(String(200), nullable=False)  # Redacted in logs
    estimated_cost = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    expected_admission_date = Column(String(50), nullable=False)
    status = Column(String(30), default="PENDING", nullable=False)  # PENDING, APPROVED, PARTIALLY_APPROVED, REJECTED, QUERY_RAISED
    policy_version_tag = Column(String(50), default="v1.0.0", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PreAuthDecisionModel(Base):
    """Append-only audit record of pre-auth decisions."""
    __tablename__ = "pre_auth_decisions"

    id = Column(Integer, primary_key=True, index=True)
    pre_auth_id = Column(String(50), index=True, nullable=False)
    decision = Column(String(30), nullable=False)
    approved_amount = Column(Numeric(12, 2, asdecimal=True), default=Decimal("0.00"), nullable=False)
    reason_codes_json = Column(Text, default="[]", nullable=False)
    decider_type = Column(String(30), default="AUTO", nullable=False)  # AUTO, MANUAL, OVERRIDE
    decider_id = Column(String(50), default="SYSTEM", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def reason_codes(self):
        return json.loads(self.reason_codes_json or "[]")

    @reason_codes.setter
    def reason_codes(self, value):
        self.reason_codes_json = json.dumps(value or [])


class ClaimModel(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), unique=True, index=True, nullable=False)
    member_id = Column(String(50), index=True, nullable=False)
    policy_id = Column(String(50), index=True, nullable=False)
    hospital_id = Column(String(50), index=True, nullable=False)
    pre_auth_id = Column(String(50), nullable=True)
    status = Column(String(30), default="PRE_AUTH", nullable=False)  # PRE_AUTH, ADMITTED, DISCHARGED, SETTLED, DISPUTED, CLOSED
    policy_version_tag = Column(String(50), default="v1.0.0", nullable=False)
    is_settled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AdmissionModel(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), unique=True, index=True, nullable=False)
    admission_date = Column(String(50), nullable=False)
    discharge_date = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ProcedureRecordModel(Base):
    __tablename__ = "procedure_records"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), index=True, nullable=False)
    procedure_name = Column(String(150), nullable=False)
    procedure_code = Column(String(50), nullable=False)
    cost = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FinalBillModel(Base):
    """Append-only record of hospital final bills."""
    __tablename__ = "final_bills"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), index=True, nullable=False)
    total_bill_amount = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    itemized_summary_json = Column(Text, default="{}", nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SettlementModel(Base):
    """Append-only record of claim settlements."""
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(String(50), unique=True, index=True, nullable=False)
    claim_id = Column(String(50), index=True, nullable=False)
    pre_auth_amount = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    final_bill = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    buffer_percentage = Column(Numeric(5, 4, asdecimal=True), nullable=False)
    bill_cap = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    effective_bill = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    deductible = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    co_pay = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    settlement_amount = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    patient_responsibility = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    status = Column(String(30), default="SETTLED", nullable=False)
    settled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ClaimTimelineEventModel(Base):
    """Append-only ledger of claim lifecycle milestones."""
    __tablename__ = "claim_timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), index=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    actor_role = Column(String(30), nullable=False)
    actor_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditEventModel(Base):
    """Append-only immutable audit trail for compliance and NFR-02."""
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    actor_role = Column(String(30), nullable=False)
    actor_id = Column(String(50), nullable=False)
    changes_json = Column(Text, default="{}", nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NotificationModel(Base):
    """Stubbed notification log for AC-09."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_type = Column(String(30), nullable=False)
    recipient_id = Column(String(50), nullable=False)
    channel = Column(String(20), default="IN_APP", nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PolicyProductConfigModel(Base):
    """Configuration for policy products and auto-approval thresholds."""
    __tablename__ = "policy_product_configs"

    id = Column(Integer, primary_key=True, index=True)
    policy_code = Column(String(50), unique=True, index=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    default_sum_insured = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    auto_approval_threshold = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    buffer_percentage = Column(Numeric(5, 4, asdecimal=True), nullable=False)
    auto_approved_diagnoses_json = Column(Text, default="[]", nullable=False)
    exclusions_json = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def auto_approved_diagnoses(self):
        return json.loads(self.auto_approved_diagnoses_json or "[]")

    @auto_approved_diagnoses.setter
    def auto_approved_diagnoses(self, value):
        self.auto_approved_diagnoses_json = json.dumps(value or [])

    @property
    def exclusions(self):
        return json.loads(self.exclusions_json or "[]")

    @exclusions.setter
    def exclusions(self, value):
        self.exclusions_json = json.dumps(value or [])


class PolicyRuleVersionModel(Base):
    """
    Immutable versioned policy rule definition (Section 7, NET-02).
    Historical claims reference the policy_version_tag active when the pre-auth was initiated.
    """
    __tablename__ = "policy_rule_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(100), unique=True, index=True, nullable=False)
    policy_code = Column(String(50), index=True, nullable=False)
    version_tag = Column(String(50), nullable=False)
    effective_from = Column(String(50), nullable=False)
    effective_to = Column(String(50), nullable=True)
    auto_approval_threshold = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    buffer_percentage = Column(Numeric(5, 4, asdecimal=True), nullable=False)
    policy_cap = Column(Numeric(12, 2, asdecimal=True), nullable=False)
    auto_approved_diagnoses_json = Column(Text, default="[]", nullable=False)
    exclusions_json = Column(Text, default="[]", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def auto_approved_diagnoses(self):
        return json.loads(self.auto_approved_diagnoses_json or "[]")

    @auto_approved_diagnoses.setter
    def auto_approved_diagnoses(self, value):
        self.auto_approved_diagnoses_json = json.dumps(value or [])

    @property
    def exclusions(self):
        return json.loads(self.exclusions_json or "[]")

    @exclusions.setter
    def exclusions(self, value):
        self.exclusions_json = json.dumps(value or [])

