# Sprint 10 Contract — Database Migrations & Policy Rule Versioning (Priority 3 & 3B)
**Sprint**: Sprint 10  
**Target Acceptance Criteria**: Section 6 (Migrations), Section 7 (Policy Versioning), NFR-02, NFR-05  
**Associated Specifications**: `specs/app_spec.md`, `specs/network_admin_spec.md`  
**Primary Agent**: `generator.md`, `test-engineer.md`  
**Reviewer Agent**: `evaluator.md`  
**Branch**: `feat/sprint-10-migrations-policy-versioning`  

---

## 1. Scope & Deliverables
1. **Alembic Database Migration Infrastructure (`alembic.ini`, `migrations/`)**:
   - Standardized `alembic.ini` and `migrations/env.py`.
   - Forward-only, append-only initial migration version `001_initial_schema.py`.
   - Migration runner function `run_migrations()` callable programmatically from startup script.
   - Verification test `tests/unit/test_migrations.py` proving an empty database can be migrated to `head` and seeded cleanly.
2. **Persistent Policy Rule Versioning Entity (`src/repositories/models.py`)**:
   - `PolicyRuleVersionModel`: `version_id`, `policy_code`, `version_tag`, `effective_from`, `effective_to`, `auto_approval_threshold`, `buffer_percentage`, `policy_cap`, `auto_approved_diagnoses_json`, `exclusions_json`, `is_active`.
   - Link `PreAuthModel` and `ClaimModel` to historical `policy_version_tag`.
3. **Historical Claim Invariance Under Versioning**:
   - Pre-auth evaluation pins decisions to the active policy version at time of submission.
   - Creating a new policy version (e.g. lowering threshold or changing whitelist) does NOT alter the evaluation or settlement of claims created under the prior policy version.
4. **Executable Tests**:
   - `tests/unit/test_migrations.py` — Verifies migration execution against empty SQLite DB.
   - `tests/unit/test_policy_versioning.py` — Proves historical claims remain bound to old version when new version is activated.
