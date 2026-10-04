# Custom Command: /implement-feature

## Description
Dispatches a tightly scoped, token-optimized implementation task to a Claude Code agent.

## Arguments
- `ac_id`: The exact Acceptance Criteria ID (e.g. `AC-07`)
- `spec_path`: The relevant specification file (e.g. `specs/settlement_spec.md`)
- `agent`: The assigned agent (e.g. `settlement-agent`)

## Execution Flow
1. Verify feature branch is active (`feat/*`).
2. Generate task prompt following Section 39 Token Optimization template.
3. Generator agent writes test first (Red phase) and validates failure.
4. Generator agent implements minimal production code (Green phase).
5. Generator agent refactors code and verifies hooks.
6. Evaluator validates acceptance criteria and prepares PR.
