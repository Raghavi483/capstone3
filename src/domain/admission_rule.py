"""
Domain Layer: Admission & Final Bill Buffer Rules (AC-06)
Enforces buffer percentage constraints on hospital bills and procedure records.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class ProcedureItem:
    """AC-06: Individual medical procedure record."""
    procedure_code: str
    description: str
    cost: Decimal

    def __post_init__(self):
        if not isinstance(self.cost, Decimal):
            raise TypeError("cost must be Decimal")
        if self.cost < Decimal("0.00"):
            raise ValueError("cost cannot be negative")


@dataclass
class BillBufferValidationResult:
    """AC-06: Outcome of bill buffer cap check."""
    is_valid: bool
    bill_cap: Decimal
    effective_bill: Decimal
    excess_amount: Decimal
    reason_codes: List[str]


def validate_final_bill_buffer(
    pre_auth_amount: Decimal,
    final_bill: Decimal,
    buffer_percentage: Decimal = Decimal("0.10")
) -> BillBufferValidationResult:
    """
    AC-06 & specs/settlement_spec.md v1.1.0:
    buffer_amount = pre_auth_amount * buffer_percentage
    bill_cap = pre_auth_amount + buffer_amount
    effective_bill = min(final_bill, bill_cap)
    excess_amount = max(0, final_bill - bill_cap)
    """
    if not isinstance(pre_auth_amount, Decimal):
        raise TypeError("pre_auth_amount must be Decimal")
    if not isinstance(final_bill, Decimal):
        raise TypeError("final_bill must be Decimal")
    if not isinstance(buffer_percentage, Decimal):
        raise TypeError("buffer_percentage must be Decimal")

    buffer_amount = (pre_auth_amount * buffer_percentage).quantize(Decimal("0.01"))
    bill_cap = (pre_auth_amount + buffer_amount).quantize(Decimal("0.01"))
    effective_bill = min(final_bill, bill_cap).quantize(Decimal("0.01"))
    excess_amount = max(Decimal("0.00"), final_bill - bill_cap).quantize(Decimal("0.01"))
    is_valid = final_bill <= bill_cap

    reason_codes: List[str] = []
    if not is_valid:
        reason_codes.append("BILL_EXCEEDS_BUFFER_CAP")

    return BillBufferValidationResult(
        is_valid=is_valid,
        bill_cap=bill_cap,
        effective_bill=effective_bill,
        excess_amount=excess_amount,
        reason_codes=reason_codes
    )
