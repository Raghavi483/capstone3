# Custom Command: /security-review

## Description
Performs an automated security, privacy, and role isolation audit across the repository.

## Execution Flow
1. Execute PHI redaction scanner (`.claude/hooks/phi-redaction-check`) across recent commits and logging statements.
2. Execute role boundary checker (`.claude/hooks/role-boundary-check`) to verify controller authorization decorators.
3. Validate that hospital endpoints isolate multi-tenant data access.
4. Output structured audit report.
