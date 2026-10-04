"""
Domain Layer: Claim State Machine & Immutability Rules (AC-08)
Enforces strict lifecycle progression:
PRE_AUTH -> ADMITTED -> DISCHARGED -> SETTLED / DISPUTED -> CLOSED
Invalid transitions raise InvalidClaimStateException.
Settled claims are immutable.
"""

from enum import Enum
from typing import Set, Dict


class InvalidClaimStateException(Exception):
    """Raised when an illegal claim state transition is attempted."""
    pass


class SettledClaimImmutableException(Exception):
    """Raised when mutation of a settled claim is attempted."""
    pass


class ClaimState(str, Enum):
    PRE_AUTH = "PRE_AUTH"
    ADMITTED = "ADMITTED"
    DISCHARGED = "DISCHARGED"
    SETTLED = "SETTLED"
    DISPUTED = "DISPUTED"
    CLOSED = "CLOSED"


VALID_CLAIM_TRANSITIONS: Dict[ClaimState, Set[ClaimState]] = {
    ClaimState.PRE_AUTH: {ClaimState.ADMITTED},
    ClaimState.ADMITTED: {ClaimState.DISCHARGED},
    ClaimState.DISCHARGED: {ClaimState.SETTLED, ClaimState.DISPUTED},
    ClaimState.SETTLED: {ClaimState.CLOSED},
    ClaimState.DISPUTED: {ClaimState.CLOSED},
    ClaimState.CLOSED: set(),
}


def validate_claim_transition(current_state: str, new_state: str) -> str:
    """
    AC-08: Validates claim state progression.
    Raises InvalidClaimStateException on illegal or backward transitions.
    Raises SettledClaimImmutableException on settled claim tampering.
    """
    try:
        curr_enum = ClaimState(current_state)
        new_enum = ClaimState(new_state)
    except ValueError as e:
        raise InvalidClaimStateException(f"Unrecognized claim state: {e}")

    # Immutability Check: Settled claim cannot transition back or alter
    if curr_enum == ClaimState.SETTLED and new_enum != ClaimState.CLOSED:
        raise SettledClaimImmutableException("Settled claim is immutable")

    allowed = VALID_CLAIM_TRANSITIONS.get(curr_enum, set())
    if new_enum not in allowed:
        raise InvalidClaimStateException(
            f"Cannot transition claim from {curr_enum.value} to {new_enum.value}"
        )

    return new_enum.value
