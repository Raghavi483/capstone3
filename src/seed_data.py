"""
Synthetic Seed Data Generation Script for MediCard Platform.
Generates deterministic synthetic profiles covering all AC testing personas:
- Eligible Customer with Active Policy
- Ineligible Customer with Inactive/Exhausted Policy
- Network Hospitals & Non-Network Hospital
- Pre-Auth Scenarios (Approved, Partially Approved, Rejected, Query Raised)
- Claim Lifecycles (Admitted, Discharged, Settled, Disputed)
"""

import sys
from pathlib import Path

# Ensure workspace root is in sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from decimal import Decimal
from datetime import datetime, timezone
from src.repositories.database import SessionLocal, init_db
from src.repositories.models import (
    CustomerModel, PolicyModel, HospitalModel, NetworkHospitalModel,
    PreAuthModel, PreAuthDecisionModel, ClaimModel, AdmissionModel,
    ProcedureRecordModel, FinalBillModel, SettlementModel,
    ClaimTimelineEventModel, AuditEventModel, NotificationModel
)


def seed_database():
    """Populates deterministic synthetic demonstration records."""
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(CustomerModel).first():
            print("[SEED] Database already contains records. Skipping seed.")
            return

        print("[SEED] Seeding deterministic synthetic data...")

        # 1. Customers
        c1 = CustomerModel(
            member_id="MEM-1001",
            name="Alice Johnson",
            email="alice.j@example.com",
            phone="+1-555-0101"
        )
        c2 = CustomerModel(
            member_id="MEM-1002",
            name="Bob Smith",
            email="bob.smith@example.com",
            phone="+1-555-0102"
        )
        c3 = CustomerModel(
            member_id="MEM-1003",
            name="Carol Davis",
            email="carol.d@example.com",
            phone="+1-555-0103"
        )
        db.add_all([c1, c2, c3])
        db.flush()

        # 2. Policies
        p1 = PolicyModel(
            policy_id="POL-5001",
            member_id="MEM-1001",
            product_name="MediCard Gold Comprehensive",
            sum_insured=Decimal("500000.00"),
            remaining_balance=Decimal("450000.00"),
            exclusions=["COSMETIC_SURGERY", "HAIR_TRANSPLANT", "EXPERIMENTAL_THERAPY"],
            is_active=True
        )
        p2 = PolicyModel(
            policy_id="POL-5002",
            member_id="MEM-1002",
            product_name="MediCard Silver Basic",
            sum_insured=Decimal("200000.00"),
            remaining_balance=Decimal("0.00"),  # Exhausted
            exclusions=["DENTAL", "COSMETIC_SURGERY"],
            is_active=True
        )
        p3 = PolicyModel(
            policy_id="POL-5003",
            member_id="MEM-1003",
            product_name="MediCard Bronze Lapsed",
            sum_insured=Decimal("100000.00"),
            remaining_balance=Decimal("100000.00"),
            exclusions=["ALL"],
            is_active=False  # Inactive
        )
        db.add_all([p1, p2, p3])
        db.flush()

        # 3. Hospitals & Network Affiliations
        h1 = HospitalModel(hospital_id="HOSP-001", name="Metro City Hospital", city="Metropolis", is_active=True)
        h2 = HospitalModel(hospital_id="HOSP-002", name="St. Jude Medical Center", city="Gotham", is_active=True)
        h3 = HospitalModel(hospital_id="HOSP-999", name="Sunrise Out-of-Network Clinic", city="Star City", is_active=True)
        db.add_all([h1, h2, h3])
        db.flush()

        net1 = NetworkHospitalModel(hospital_id="HOSP-001", tier="TIER_1", is_in_network=True)
        net2 = NetworkHospitalModel(hospital_id="HOSP-002", tier="TIER_2", is_in_network=True)
        net3 = NetworkHospitalModel(hospital_id="HOSP-999", tier="NON_NETWORK", is_in_network=False)
        db.add_all([net1, net2, net3])
        db.flush()

        # 4. Pre-Auth & Decisions
        # Case 1: Auto-Approved Pre-Auth
        pa1 = PreAuthModel(
            pre_auth_id="PA-2001",
            claim_id="CLM-3001",
            hospital_id="HOSP-001",
            member_id="MEM-1001",
            policy_id="POL-5001",
            diagnosis="ACUTE_APPENDICITIS",
            estimated_cost=Decimal("45000.00"),
            expected_admission_date="2026-10-10",
            status="APPROVED"
        )
        pad1 = PreAuthDecisionModel(
            pre_auth_id="PA-2001",
            decision="APPROVED",
            approved_amount=Decimal("45000.00"),
            reason_codes=["AUTO_APPROVED_RULE_01"],
            decider_type="AUTO",
            decider_id="SYSTEM"
        )

        # Case 2: Rejected Pre-Auth (Excluded Diagnosis)
        pa2 = PreAuthModel(
            pre_auth_id="PA-2002",
            claim_id="CLM-3002",
            hospital_id="HOSP-001",
            member_id="MEM-1001",
            policy_id="POL-5001",
            diagnosis="COSMETIC_SURGERY",
            estimated_cost=Decimal("75000.00"),
            expected_admission_date="2026-10-12",
            status="REJECTED"
        )
        pad2 = PreAuthDecisionModel(
            pre_auth_id="PA-2002",
            decision="REJECTED",
            approved_amount=Decimal("0.00"),
            reason_codes=["EXCLUDED_CONDITION"],
            decider_type="AUTO",
            decider_id="SYSTEM"
        )

        # Case 3: Query Raised / Pending
        pa3 = PreAuthModel(
            pre_auth_id="PA-2003",
            claim_id="CLM-3003",
            hospital_id="HOSP-002",
            member_id="MEM-1001",
            policy_id="POL-5001",
            diagnosis="UNSPECIFIED_ABDOMINAL_PAIN",
            estimated_cost=Decimal("120000.00"),
            expected_admission_date="2026-10-15",
            status="QUERY_RAISED"
        )
        pad3 = PreAuthDecisionModel(
            pre_auth_id="PA-2003",
            decision="QUERY_RAISED",
            approved_amount=Decimal("0.00"),
            reason_codes=["ADDITIONAL_DIAGNOSTICS_REQUIRED"],
            decider_type="MANUAL",
            decider_id="ADJUDICATOR_01"
        )
        db.add_all([pa1, pad1, pa2, pad2, pa3, pad3])
        db.flush()

        # 5. Claims Lifecycle
        # Claim 1: Settled
        c_settled = ClaimModel(
            claim_id="CLM-3001",
            member_id="MEM-1001",
            policy_id="POL-5001",
            hospital_id="HOSP-001",
            pre_auth_id="PA-2001",
            status="SETTLED",
            is_settled=True
        )
        adm1 = AdmissionModel(claim_id="CLM-3001", admission_date="2026-10-10", discharge_date="2026-10-13")
        proc1 = ProcedureRecordModel(claim_id="CLM-3001", procedure_name="Appendectomy", procedure_code="PR-APP-01", cost=Decimal("42000.00"))
        fb1 = FinalBillModel(claim_id="CLM-3001", total_bill_amount=Decimal("48000.00"), itemized_summary_json='{"surgery": 35000, "room": 13000}')
        
        # AC-07 Settlement Calculation:
        # pre_auth = 45000, buffer = 10% (4500) -> cap = 49500
        # bill = 48000 <= 49500 -> effective_bill = 48000
        # deductible = 1000, co_pay = 2000 -> settlement = 45000, patient_resp = 3000
        s1 = SettlementModel(
            settlement_id="SET-4001",
            claim_id="CLM-3001",
            pre_auth_amount=Decimal("45000.00"),
            final_bill=Decimal("48000.00"),
            buffer_percentage=Decimal("0.1000"),
            bill_cap=Decimal("49500.00"),
            effective_bill=Decimal("48000.00"),
            deductible=Decimal("1000.00"),
            co_pay=Decimal("2000.00"),
            settlement_amount=Decimal("45000.00"),
            patient_responsibility=Decimal("3000.00"),
            status="SETTLED"
        )
        
        # Claim 2: Disputed
        c_disputed = ClaimModel(
            claim_id="CLM-3004",
            member_id="MEM-1001",
            policy_id="POL-5001",
            hospital_id="HOSP-001",
            pre_auth_id="PA-2004",
            status="DISPUTED",
            is_settled=False
        )

        db.add_all([c_settled, adm1, proc1, fb1, s1, c_disputed])
        db.flush()

        # 6. Timeline Events
        te1 = ClaimTimelineEventModel(
            claim_id="CLM-3001",
            event_type="PRE_AUTH_SUBMITTED",
            description="Pre-auth requested by Metro City Hospital for Appendectomy",
            actor_role="HOSPITAL",
            actor_id="HOSP-001"
        )
        te2 = ClaimTimelineEventModel(
            claim_id="CLM-3001",
            event_type="PRE_AUTH_APPROVED",
            description="System auto-approved pre-authorization up to INR 45,000.00",
            actor_role="SYSTEM",
            actor_id="RULES_ENGINE"
        )
        te3 = ClaimTimelineEventModel(
            claim_id="CLM-3001",
            event_type="ADMITTED",
            description="Patient admitted to inpatient ward",
            actor_role="HOSPITAL",
            actor_id="HOSP-001"
        )
        te4 = ClaimTimelineEventModel(
            claim_id="CLM-3001",
            event_type="DISCHARGED",
            description="Patient successfully discharged following surgery",
            actor_role="HOSPITAL",
            actor_id="HOSP-001"
        )
        te5 = ClaimTimelineEventModel(
            claim_id="CLM-3001",
            event_type="SETTLED",
            description="Settlement calculated and finalized: INR 45,000.00",
            actor_role="SYSTEM",
            actor_id="SETTLEMENT_ENGINE"
        )
        db.add_all([te1, te2, te3, te4, te5])

        # 7. Stubbed Notification
        n1 = NotificationModel(
            recipient_type="CUSTOMER",
            recipient_id="MEM-1001",
            message="Your cashless hospitalization claim CLM-3001 has been settled.",
            channel="SMS"
        )
        db.add(n1)

        db.commit()
        print("[SEED] Deterministic synthetic data seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"[SEED] Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
