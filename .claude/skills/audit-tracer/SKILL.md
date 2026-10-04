---
name: audit-tracer
description: Formulates immutable, append-only audit events and verifies PHI redaction
---

# Skill: audit-tracer

## Purpose
Constructs append-only audit entries for all pre-auth decisions, final bill submissions, settlement payouts, and administrator overrides while ensuring patient PHI is completely scrubbed.

## Inputs
- `case_id` (string)
- `actor_id` (string)
- `actor_role` (string)
- `action` (string)
- `details` (dict)

## Execution Logic & Rules
1. Inspect `details` dictionary for any clinical PHI fields (`diagnosis`, `procedure`, `medical_notes`, `health_history`).
2. Replace sensitive values with SHA-256 hash or tokenized identifier (`[REDACTED_PHI]`).
3. Formulate immutable audit payload with UTC ISO-8601 timestamp.
4. Persist to `audit_logs` repository using insert-only semantics.

## Outputs
- `audit_entry_id`: UUID
- `sanitized_payload`: dict
- `persisted`: boolean
