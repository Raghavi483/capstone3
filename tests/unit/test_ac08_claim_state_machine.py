"""
Test Suite: AC-08 Claim State Machine & Immutability
Acceptance Criteria:
    Claim lifecycle: PRE_AUTH -> ADMITTED -> DISCHARGED -> SETTLED / DISPUTED -> CLOSED.
    Invalid transitions MUST raise InvalidClaimStateException.
    Settled claims are immutable.
"""

import pytest
from src.domain.claim_state_rule import (
    ClaimState,
    validate_claim_transition,
    InvalidClaimStateException,
    SettledClaimImmutableException
)


def test_ac08_valid_progression_standard_path():
    """AC-08: Happy path from PRE_AUTH to CLOSED via SETTLED."""
    state = ClaimState.PRE_AUTH
    state = validate_claim_transition(state, ClaimState.ADMITTED)
    assert state == ClaimState.ADMITTED

    state = validate_claim_transition(state, ClaimState.DISCHARGED)
    assert state == ClaimState.DISCHARGED

    state = validate_claim_transition(state, ClaimState.SETTLED)
    assert state == ClaimState.SETTLED

    state = validate_claim_transition(state, ClaimState.CLOSED)
    assert state == ClaimState.CLOSED


def test_ac08_valid_progression_dispute_path():
    """AC-08: Dispute path from DISCHARGED to DISPUTED to CLOSED."""
    state = ClaimState.DISCHARGED
    state = validate_claim_transition(state, ClaimState.DISPUTED)
    assert state == ClaimState.DISPUTED

    state = validate_claim_transition(state, ClaimState.CLOSED)
    assert state == ClaimState.CLOSED


def test_ac08_invalid_transition_pre_auth_to_settled():
    """AC-08: Skipping states (PRE_AUTH directly to SETTLED) raises InvalidClaimStateException."""
    with pytest.raises(InvalidClaimStateException, match="Cannot transition claim from PRE_AUTH to SETTLED"):
        validate_claim_transition(ClaimState.PRE_AUTH, ClaimState.SETTLED)


def test_ac08_backward_transition_raises_exception():
    """AC-08: Backward transition (DISCHARGED back to ADMITTED) raises InvalidClaimStateException."""
    with pytest.raises(InvalidClaimStateException, match="Cannot transition claim from DISCHARGED to ADMITTED"):
        validate_claim_transition(ClaimState.DISCHARGED, ClaimState.ADMITTED)


def test_ac08_settled_claim_immutability():
    """Rule & Invariant: Settled claims cannot transition back or be mutated."""
    with pytest.raises(SettledClaimImmutableException, match="Settled claim is immutable"):
        validate_claim_transition(ClaimState.SETTLED, ClaimState.ADMITTED)
