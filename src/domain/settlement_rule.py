"""
Domain Layer: Settlement Calculator Engine (AC-07, NFR-01, NFR-02)
Authoritative implementation of the MediCard settlement formula specified in specs/settlement_spec.md v1.1.0.

Formula:
    buffer_amount = pre_auth_amount * buffer_percentage
    bill_cap = pre_auth_amount + buffer_amount
    effective_bill = min(final_bill, bill_cap)
    settlement_amount = max(0, effective_bill - deductible - co_pay)
    patient_responsibility = (final_bill - effective_bill) + deductible + co_pay

Enforces:
    - Pure Decimal arithmetic (zero float).
    - Non-negative settlement floor invariant: settlement_amount >= 0.
    - Currency quantized to 2 decimal places.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class SettlementCalculationInput:
    """AC-07: Input parameters for settlement calculation."""
    pre_auth_amount: Decimal
    final_bill: Decimal
    buffer_percentage: Decimal
    deductible: Decimal
    co_pay: Decimal
    policy_remaining_balance: Optional[Decimal] = None

    def __post_init__(self):
        for field_name in ["pre_auth_amount", "final_bill", "buffer_percentage", "deductible", "co_pay"]:
            val = getattr(self, field_name)
            if not isinstance(val, Decimal):
                raise TypeError(f"{field_name} must be Decimal")
            if val < Decimal("0.00"):
                raise ValueError(f"{field_name} cannot be negative")

        if self.policy_remaining_balance is not None:
            if not isinstance(self.policy_remaining_balance, Decimal):
                raise TypeError("policy_remaining_balance must be Decimal")
            if self.policy_remaining_balance < Decimal("0.00"):
                raise ValueError("policy_remaining_balance cannot be negative")


@dataclass
class SettlementCalculationResult:
    """AC-07: Calculation breakdown and insurer payout."""
    buffer_amount: Decimal
    bill_cap: Decimal
    effective_bill: Decimal
    deductions_total: Decimal
    settlement_amount: Decimal
    patient_responsibility: Decimal
    settlement_status: str = "SETTLED"


def calculate_settlement(inp: SettlementCalculationInput) -> SettlementCalculationResult:
    """
    AC-07: Centralized invariant-checked settlement calculation.
    """
    cent = Decimal("0.01")
    
    # 1. Buffer Amount
    buffer_amount = (inp.pre_auth_amount * inp.buffer_percentage).quantize(cent)
    
    # 2. Bill Cap
    bill_cap = (inp.pre_auth_amount + buffer_amount).quantize(cent)
    
    # 3. Effective Bill
    effective_bill = min(inp.final_bill, bill_cap).quantize(cent)
    
    # 4. Total Deductions
    deductions_total = (inp.deductible + inp.co_pay).quantize(cent)
    
    # 5. Preliminary Settlement Amount
    preliminary_settlement = max(Decimal("0.00"), effective_bill - deductions_total).quantize(cent)
    
    # 6. Policy Remaining Balance Cap (if specified)
    if inp.policy_remaining_balance is not None:
        settlement_amount = min(preliminary_settlement, inp.policy_remaining_balance).quantize(cent)
    else:
        settlement_amount = preliminary_settlement

    # 7. Patient Responsibility
    # If deductions exceed effective bill, patient responsibility is deductions_total
    # If final bill exceeds bill_cap, patient also pays the excess
    excess_over_cap = max(Decimal("0.00"), inp.final_bill - effective_bill).quantize(cent)
    if effective_bill < deductions_total:
        patient_responsibility = (excess_over_cap + deductions_total).quantize(cent)
    else:
        patient_responsibility = (inp.final_bill - settlement_amount).quantize(cent)

    # 8. Invariant Enforcement
    assert settlement_amount >= Decimal("0.00"), f"Settlement invariant violated: {settlement_amount} < 0"

    return SettlementCalculationResult(
        buffer_amount=buffer_amount,
        bill_cap=bill_cap,
        effective_bill=effective_bill,
        deductions_total=deductions_total,
        settlement_amount=settlement_amount,
        patient_responsibility=patient_responsibility,
        settlement_status="SETTLED"
    )
