"""
Test Suite: AC-07 Settlement Calculation & Invariant Enforcement
Acceptance Criteria:
    buffer_amount = pre_auth_amount * buffer_percentage
    bill_cap = pre_auth_amount + buffer_amount
    effective_bill = min(final_bill, bill_cap)
    settlement_amount = max(0, effective_bill - deductible - co_pay)
    patient_responsibility = (final_bill - effective_bill) + deductible + co_pay

Covers 10 mandatory edge case scenarios:
1. final_bill strictly below cap
2. final_bill exactly at cap
3. final_bill above cap
4. deductible deduction
5. co-pay deduction
6. deductible + co-pay > effective bill
7. zero settlement floor invariant (settlement >= 0)
8. policy cap interaction
9. rounding / precision edge cases
10. negative / invalid monetary input rejection
"""

from decimal import Decimal
import pytest
from src.domain.settlement_rule import (
    SettlementCalculationInput,
    SettlementCalculationResult,
    calculate_settlement
)


def test_ac07_case_1_final_bill_below_cap():
    """AC-07 Case 1: Final bill strictly below buffer cap."""
    # pre_auth = 50,000, buffer = 10% -> cap = 55,000, bill = 52,000
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("50000.00"),
        final_bill=Decimal("52000.00"),
        buffer_percentage=Decimal("0.10"),
        deductible=Decimal("2000.00"),
        co_pay=Decimal("5000.00")
    )
    res: SettlementCalculationResult = calculate_settlement(inp)
    assert res.buffer_amount == Decimal("5000.00")
    assert res.bill_cap == Decimal("55000.00")
    assert res.effective_bill == Decimal("52000.00")
    assert res.settlement_amount == Decimal("45000.00")
    assert res.patient_responsibility == Decimal("7000.00")
    assert res.settlement_amount + res.patient_responsibility == inp.final_bill


def test_ac07_case_2_final_bill_exactly_at_cap():
    """AC-07 Case 2: Final bill exactly equal to buffer cap."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("50000.00"),
        final_bill=Decimal("55000.00"),
        buffer_percentage=Decimal("0.10"),
        deductible=Decimal("1000.00"),
        co_pay=Decimal("4000.00")
    )
    res = calculate_settlement(inp)
    assert res.bill_cap == Decimal("55000.00")
    assert res.effective_bill == Decimal("55000.00")
    assert res.settlement_amount == Decimal("50000.00")
    assert res.patient_responsibility == Decimal("5000.00")
    assert res.settlement_amount + res.patient_responsibility == inp.final_bill


def test_ac07_case_3_final_bill_above_cap():
    """AC-07 Case 3: Final bill strictly above buffer cap."""
    # pre_auth = 100,000, buffer = 10% -> cap = 110,000, bill = 120,000
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("100000.00"),
        final_bill=Decimal("120000.00"),
        buffer_percentage=Decimal("0.10"),
        deductible=Decimal("0.00"),
        co_pay=Decimal("10000.00")
    )
    res = calculate_settlement(inp)
    assert res.bill_cap == Decimal("110000.00")
    assert res.effective_bill == Decimal("110000.00")
    assert res.settlement_amount == Decimal("100000.00")
    # Patient pays (120,000 - 110,000) excess + 10,000 co-pay = 20,000
    assert res.patient_responsibility == Decimal("20000.00")
    assert res.settlement_amount + res.patient_responsibility == inp.final_bill


def test_ac07_case_4_deductible_application():
    """AC-07 Case 4: Deductible deduction applied properly."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("30000.00"),
        final_bill=Decimal("30000.00"),
        buffer_percentage=Decimal("0.00"),
        deductible=Decimal("5000.00"),
        co_pay=Decimal("0.00")
    )
    res = calculate_settlement(inp)
    assert res.settlement_amount == Decimal("25000.00")
    assert res.patient_responsibility == Decimal("5000.00")


def test_ac07_case_5_co_pay_application():
    """AC-07 Case 5: Co-pay deduction applied properly."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("40000.00"),
        final_bill=Decimal("40000.00"),
        buffer_percentage=Decimal("0.00"),
        deductible=Decimal("0.00"),
        co_pay=Decimal("8000.00")
    )
    res = calculate_settlement(inp)
    assert res.settlement_amount == Decimal("32000.00")
    assert res.patient_responsibility == Decimal("8000.00")


def test_ac07_case_6_deductible_plus_copay_exceeds_effective_bill():
    """AC-07 Case 6: Total deductions exceed effective bill, floored at 0."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("10000.00"),
        final_bill=Decimal("10000.00"),
        buffer_percentage=Decimal("0.00"),
        deductible=Decimal("8000.00"),
        co_pay=Decimal("5000.00")  # total = 13,000 > 10,000
    )
    res = calculate_settlement(inp)
    assert res.settlement_amount == Decimal("0.00")
    assert res.settlement_amount >= Decimal("0.00")
    # Patient responsibility is 13,000 (all deductions)
    assert res.patient_responsibility == Decimal("13000.00")


def test_ac07_case_7_zero_settlement_floor_invariant():
    """AC-07 Case 7: Zero settlement invariant verification."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("5000.00"),
        final_bill=Decimal("5000.00"),
        buffer_percentage=Decimal("0.00"),
        deductible=Decimal("5000.00"),
        co_pay=Decimal("0.00")
    )
    res = calculate_settlement(inp)
    assert res.settlement_amount == Decimal("0.00")
    assert res.settlement_amount >= Decimal("0.00")


def test_ac07_case_8_policy_cap_interaction():
    """AC-07 Case 8: Policy remaining balance cap limits insurer payout."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("60000.00"),
        final_bill=Decimal("60000.00"),
        buffer_percentage=Decimal("0.00"),
        deductible=Decimal("0.00"),
        co_pay=Decimal("0.00"),
        policy_remaining_balance=Decimal("45000.00")  # Balance cap
    )
    res = calculate_settlement(inp)
    assert res.settlement_amount == Decimal("45000.00")
    assert res.patient_responsibility == Decimal("15000.00")


def test_ac07_case_9_rounding_and_precision():
    """AC-07 Case 9: Fractional cent precision quantized to exactly 2 decimal places."""
    inp = SettlementCalculationInput(
        pre_auth_amount=Decimal("33333.33"),
        final_bill=Decimal("35000.00"),
        buffer_percentage=Decimal("0.075"),  # 7.5% -> 2499.99975
        deductible=Decimal("333.33"),
        co_pay=Decimal("666.67")
    )
    res = calculate_settlement(inp)
    # Check that all outputs are quantized to 2 places
    assert res.buffer_amount == Decimal("2500.00")
    assert res.bill_cap == Decimal("35833.33")
    assert res.settlement_amount == Decimal("34000.00")


def test_ac07_case_10_negative_or_invalid_monetary_input_rejection():
    """AC-07 Case 10: Negative inputs or floating point types are rejected."""
    # Negative final bill
    with pytest.raises(ValueError, match="cannot be negative"):
        SettlementCalculationInput(
            pre_auth_amount=Decimal("50000.00"),
            final_bill=Decimal("-1000.00"),
            buffer_percentage=Decimal("0.10"),
            deductible=Decimal("0.00"),
            co_pay=Decimal("0.00")
        )

    # Float violation
    with pytest.raises(TypeError, match="must be Decimal"):
        SettlementCalculationInput(
            pre_auth_amount=50000.00,  # float violation
            final_bill=Decimal("50000.00"),
            buffer_percentage=Decimal("0.10"),
            deductible=Decimal("0.00"),
            co_pay=Decimal("0.00")
        )
