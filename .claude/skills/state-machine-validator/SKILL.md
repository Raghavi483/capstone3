---
name: state-machine-validator
description: Validates and enforces cashless claim lifecycle state transitions
---

# Skill: state-machine-validator

## Purpose
Validates whether a proposed claim transition is valid according to the MediCard state machine matrix.

## Inputs
- `current_state` (string)
- `proposed_state` (string)
- `context` (dict containing approval status, bill details, etc.)

## Execution Logic & Rules
Allowed transitions:
1. `PRE_AUTH` -> `ADMITTED` (requires pre-auth status == `APPROVED` or `OVERRIDE_APPROVED`)
2. `ADMITTED` -> `DISCHARGED` (requires final bill submitted <= cap)
3. `DISCHARGED` -> `SETTLED` (requires settlement calculation completed)
4. `DISCHARGED` -> `DISPUTED` (in case of dispute)
5. `SETTLED` -> `CLOSED`
6. `DISPUTED` -> `CLOSED`

Any other transition must raise `InvalidClaimStateException`.

## Outputs
- `is_valid`: boolean
- `error_message`: string (if invalid)
