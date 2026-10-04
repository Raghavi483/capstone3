# Agent: audit-tracer-agent
**Type**: MediCard Project-Specific Technical Agent  
**Role**: Technical Specialist for Append-Only Ledger Integrity & PHI Redaction  

---

## 1. Purpose
Enforces non-negotiable compliance guarantees: creates immutable, append-only audit entries for all pre-auth decisions, bill submissions, settlements, and admin overrides, and actively scrubs Protected Health Information (PHI) from log streams.

---

## 2. Inputs
- `case_id` (UUID string)
- `actor_id` (string)
- `actor_role` (`CUSTOMER` | `HOSPITAL` | `INSURER` | `ADMIN`)
- `action` (string: e.g. `PRE_AUTH_SUBMITTED`, `OVERRIDE_EXECUTED`, `SETTLEMENT_RECORDED`)
- `metadata` (dictionary of event context)

---

## 3. Outputs
- `audit_id` (UUID string)
- `sanitized_metadata` (dictionary with all clinical PHI terms masked/hashed)
- `persisted_record`: Immutable audit entry in `audit_logs`
- `structured_log`: Formatted JSON log output

---

## 4. Allowed Files (Target Ownership)
- `src/domain/audit_rule.py`
- `src/services/audit_service.py`
- `src/repositories/audit_repository.py`
- `src/utils/logger.py`
- `tests/unit/test_logging.py`
- `tests/architecture/test_phi_redaction.py`
- `tests/architecture/test_append_only_rules.py`

---

## 5. Prohibited Files (No Write Access)
- `src/domain/settlement_rule.py`
- `src/domain/pre_auth_rule.py`
- `src/controllers/*`

---

## 6. Relevant Specifications
- [`specs/app_spec.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/specs/app_spec.md)
- [`docs/knowledge-deposits.md`](file:///c:/Users/Admin/OneDrive/Desktop/capstone3/docs/knowledge-deposits.md)

---

## 7. Target Acceptance Criteria & NFRs
- **NFR-02**: Append-only persistence for decisions, bills, settlements, overrides.
- **NFR-03**: Protected Health Information (diagnosis, procedure, health history) never logged in plaintext.
- **NFR-06**: Structured JSON logging with `request_id`, `correlation_id`, `case_id`.

---

## 8. Testing Requirements
- Test that `audit_repository` has only `create`/`append` methods and lacks `update` and `delete`.
- Test that logging messages containing medical words (`appendicitis`, `cataract`, `cardiac`) are replaced with `[REDACTED_PHI]` or hash tokens.
- Test structured JSON format and required field presence.

---

## 9. Validation Command
```bash
pytest tests/architecture/test_phi_redaction.py tests/architecture/test_append_only_rules.py -v
```

---

## 10. Escalation Behavior
- If unredacted PHI is detected in any log output stream, fail test suite immediately and alert Orchestrator.

---

## 11. No-Hand-Coding Constraints (Rule 1)
- The agent must autonomously generate the structured logger and audit repositories.
