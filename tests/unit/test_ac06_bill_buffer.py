"""
Test Suite: AC-06 Hospital Post-Admission Updates & Final Bill Buffer
Acceptance Criteria:
    Hospital submits procedure details and final bill.
    Final bill cannot exceed pre_auth_amount + configured buffer.
"""

from decimal import Decimal
import pytest
from src.domain.admission_rule import (
    validate_final_bill_buffer,
    BillBufferValidationResult,
    ProcedureItem
)


def test_ac06_bill_within_buffer_accepted():
    """AC-06 Scenario 1: Bill of 53,000 within 50,000 + 10% buffer (55,000 cap) is accepted."""
    result: BillBufferValidationResult = validate_final_bill_buffer(
        pre_auth_amount=Decimal("50000.00"),
        final_bill=Decimal("53000.00"),
        buffer_percentage=Decimal("0.10")
    )
    assert result.is_valid is True
    assert result.bill_cap == Decimal("55000.00")
    assert result.effective_bill == Decimal("53000.00")
    assert result.excess_amount == Decimal("0.00")


def test_ac06_bill_exceeding_buffer_flagged():
    """AC-06 Scenario 2: Bill of 62,000 exceeding 55,000 buffer cap is flagged and capped."""
    result: BillBufferValidationResult = validate_final_bill_buffer(
        pre_auth_amount=Decimal("50000.00"),
        final_bill=Decimal("62000.00"),
        buffer_percentage=Decimal("0.10")
    )
    assert result.is_valid is False
    assert result.bill_cap == Decimal("55000.00")
    assert result.effective_bill == Decimal("55000.00")  # Capped at bill_cap
    assert result.excess_amount == Decimal("7000.00")
    assert "BILL_EXCEEDS_BUFFER_CAP" in result.reason_codes


def test_ac06_float_rejection():
    """NFR-01: Prohibits float for bill calculations."""
    with pytest.raises(TypeError, match="must be Decimal"):
        validate_final_bill_buffer(
            pre_auth_amount=50000.00,  # float violation
            final_bill=Decimal("53000.00"),
            buffer_percentage=Decimal("0.10")
        )


def test_ac06_procedure_item_decimal_validation():
    """AC-06: Procedure record validates code, name, and Decimal cost."""
    proc = ProcedureItem(
        procedure_code="PR-APP-01",
        description="Laparoscopic Appendectomy",
        cost=Decimal("42000.00")
    )
    assert proc.procedure_code == "PR-APP-01"
    assert proc.cost == Decimal("42000.00")
