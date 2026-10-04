# Test-Driven Development (TDD) Strategy & Worked Example
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Methodology**: Red-Green-Refactor with Automated Agent Verification  

---

## 1. Core TDD Philosophy in AI-Native Engineering

In the MediCard platform, Test-Driven Development (TDD) is not an afterthought—it is the primary instrument of specification enforcement. Because production code is generated strictly by Claude Code agents under **Rule 1 (No Hand-Coding)**, automated tests define the unambiguous boundaries that generated code must satisfy.

The development lifecycle enforces the **Red-Green-Refactor** discipline:

```
        +-------------------------------------------------------+
        |                 1. RED PHASE (Failing)                |
        | Test Engineer generates targeted test based on AC-NN  |
        | Test runs and FAILS against current code / interface  |
        +-------------------------------------------------------+
                                   |
                                   v
        +-------------------------------------------------------+
        |                 2. GREEN PHASE (Passing)              |
        | Generator agent implements minimal production code    |
        | Test runs and PASSES (all invariants satisfied)       |
        +-------------------------------------------------------+
                                   |
                                   v
        +-------------------------------------------------------+
        |               3. REFACTOR PHASE (Clean Code)          |
        | Generator refactors for readability, removes dups     |
        | Architecture tests confirm layer boundaries hold      |
        +-------------------------------------------------------+
```

---

## 2. Worked Example: AC-07 Settlement Calculation & Buffer Edge Cases

### 2.1 The Specification Requirements (from `specs/settlement_spec.md`)
- **Formula**:
  $$\text{bill\_cap} = \text{pre\_auth\_amount} \times (1 + \text{buffer\_percentage})$$
  $$\text{effective\_bill} = \min(\text{final\_bill}, \text{bill\_cap})$$
  $$\text{settlement\_amount} = \max(0, \text{effective\_bill} - \text{deductible} - \text{co\_pay})$$
- **Invariants**:
  1. $\text{settlement\_amount} \ge 0$.
  2. Fixed-point precision using Python `decimal.Decimal` (never `float`).
  3. Final bill exceeding pre-auth + buffer must be capped or rejected as invalid per AC-06.

---

### 2.2 Phase 1: RED (Test Generation Prior to Implementation)

The test engineer agent specifies test scenarios spanning typical and extreme boundary cases:

```python
# tests/unit/test_ac07_settlement.py
import pytest
from decimal import Decimal
from src.domain.settlement_rule import calculate_settlement, SettlementCalculationInput

def test_ac07_standard_settlement():
    """AC-07: Standard settlement calculation with deductible and co-pay."""
    calc_input = SettlementCalculationInput(
        final_bill=Decimal("50000.00"),
        pre_auth_amount=Decimal("50000.00"),
        buffer_percentage=Decimal("0.10"),  # 10% buffer = cap of 55000.00
        deductible=Decimal("2000.00"),
        co_pay=Decimal("5000.00")
    )
    result = calculate_settlement(calc_input)
    # effective_bill = min(50000, 55000) = 50000
    # settlement = 50000 - 2000 - 5000 = 43000.00
    assert result.settlement_amount == Decimal("43000.00")
    assert result.settlement_amount >= Decimal("0.00")

def test_ac07_final_bill_exceeds_pre_auth_but_within_buffer():
    """AC-07: Final bill exceeds pre-auth amount but remains within 10% buffer."""
    calc_input = SettlementCalculationInput(
        final_bill=Decimal("54000.00"),
        pre_auth_amount=Decimal("50000.00"),
        buffer_percentage=Decimal("0.10"),  # cap = 55000.00
        deductible=Decimal("1000.00"),
        co_pay=Decimal("0.00")
    )
    result = calculate_settlement(calc_input)
    # effective_bill = 54000.00
    # settlement = 54000 - 1000 = 53000.00
    assert result.settlement_amount == Decimal("53000.00")

def test_ac07_final_bill_exceeds_buffer_cap():
    """AC-07: Final bill exceeds pre-auth + buffer; bill is capped at max allowed."""
    calc_input = SettlementCalculationInput(
        final_bill=Decimal("65000.00"),
        pre_auth_amount=Decimal("50000.00"),
        buffer_percentage=Decimal("0.10"),  # cap = 55000.00
        deductible=Decimal("0.00"),
        co_pay=Decimal("5000.00")
    )
    result = calculate_settlement(calc_input)
    # effective_bill = min(65000, 55000) = 55000
    # settlement = 55000 - 5000 = 50000.00
    assert result.settlement_amount == Decimal("50000.00")

def test_ac07_deductible_and_copay_exceed_bill_invariant():
    """AC-07: High deductible/co-pay cannot cause negative settlement (must be >= 0)."""
    calc_input = SettlementCalculationInput(
        final_bill=Decimal("10000.00"),
        pre_auth_amount=Decimal("10000.00"),
        buffer_percentage=Decimal("0.00"),
        deductible=Decimal("8000.00"),
        co_pay=Decimal("5000.00")  # total deductions = 13000 > 10000
    )
    result = calculate_settlement(calc_input)
    assert result.settlement_amount == Decimal("0.00")
    assert result.settlement_amount >= Decimal("0.00")

def test_ac07_enforce_decimal_types():
    """NFR-01: Prohibit float inputs to ensure fixed-point accuracy."""
    with pytest.raises(TypeError, match="must be Decimal"):
        calculate_settlement(SettlementCalculationInput(
            final_bill=50000.00,  # float error!
            pre_auth_amount=Decimal("50000.00"),
            buffer_percentage=Decimal("0.10"),
            deductible=Decimal("0.00"),
            co_pay=Decimal("0.00")
        ))
```

*Execution Result*: `ModuleNotFoundError: No module named 'src.domain.settlement_rule'`. **RED PHASE CONFIRMED.**

---

### 2.3 Phase 2: GREEN (Minimal Generator Implementation)

The generator agent implements the domain rule module with zero external dependencies:

```python
# src/domain/settlement_rule.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class SettlementCalculationInput:
    final_bill: Decimal
    pre_auth_amount: Decimal
    buffer_percentage: Decimal
    deductible: Decimal
    co_pay: Decimal

    def __post_init__(self):
        for field_name, val in self.__dict__.items():
            if not isinstance(val, Decimal):
                raise TypeError(f"Field '{field_name}' must be Decimal, got {type(val).__name__}")
            if val < Decimal("0.00"):
                raise ValueError(f"Field '{field_name}' cannot be negative")

@dataclass(frozen=True)
class SettlementResult:
    effective_bill: Decimal
    settlement_amount: Decimal
    capped_amount: Decimal
    deductions_applied: Decimal

def calculate_settlement(input_data: SettlementCalculationInput) -> SettlementResult:
    bill_cap = input_data.pre_auth_amount * (Decimal("1.00") + input_data.buffer_percentage)
    effective_bill = min(input_data.final_bill, bill_cap)
    total_deductions = input_data.deductible + input_data.co_pay
    raw_settlement = effective_bill - total_deductions
    settlement_amount = max(Decimal("0.00"), raw_settlement)
    
    return SettlementResult(
        effective_bill=effective_bill,
        settlement_amount=settlement_amount,
        capped_amount=bill_cap,
        deductions_applied=total_deductions
    )
```

*Execution Result*: `5 passed in 0.04s`. **GREEN PHASE CONFIRMED.**

---

### 2.4 Phase 3: REFACTOR (Structural Cleanliness & Optimization)

- Refactored `calculate_settlement` to return a frozen, immutable dataclass containing breakdown telemetry (`effective_bill`, `capped_amount`, `deductions_applied`).
- Verified zero floating-point conversions.
- Passed local `settlement-cap-check` hook.

---

## 3. Targeted Test File Distribution Plan (≥ 10 Test Files)

To demonstrate rigorous TDD progression across development history, the test suite is partitioned into focused test suites:

1. `tests/unit/test_ac01_policy_coverage.py` — Customer registration & policy coverage visibility
2. `tests/unit/test_ac02_eligibility.py` — Hospital member eligibility lookup and standardized reason codes
3. `tests/unit/test_ac03_preauth_submission.py` — Pre-auth intake validation and initial PENDING state
4. `tests/unit/test_ac04_preauth_lifecycle.py` — State transitions across APPROVED, PARTIALLY_APPROVED, REJECTED, QUERY_RAISED
5. `tests/unit/test_ac05_auto_approval.py` — Low-cost threshold and diagnosis white-list auto-decisioning
6. `tests/unit/test_ac06_bill_submission.py` — Post-admission procedure tracking and final bill buffer limits
7. `tests/unit/test_ac07_settlement.py` — Fixed-point decimal arithmetic, co-pay/deductible, and zero-floor invariant
8. `tests/unit/test_ac08_claim_state_machine.py` — State machine progression and `InvalidClaimStateException`
9. `tests/unit/test_ac09_notifications.py` — Transition event generation and timeline assembly
10. `tests/unit/test_ac10_admin_override.py` — Insurer admin override authorization, justification, and audit logging
11. `tests/architecture/test_layer_dependencies.py` — Layering isolation rules (domain has 0 outer dependencies)
12. `tests/architecture/test_phi_redaction.py` — PHI log scrubbing verification
13. `tests/architecture/test_append_only_rules.py` — Immutability verification of audit and decision ledgers
