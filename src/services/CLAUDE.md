# CLAUDE.md — Service Layer Directives (`src/services/`)

## 1. Orchestration & Boundaries
- The service layer coordinates application use cases, coordinates repository persistence, and triggers event notifications.
- Services may import from:
  - `src/domain/` (pure rules and entities)
  - `src/repositories/` (data access interfaces)
  - `src/utils/` (logging, notifications)
- Services MUST NOT import from `src/controllers/` or handle HTTP status codes directly.

## 2. Mandatory Responsibilities
- **AC-09 (Stubbed Notifications)**: Every successful state transition must call the notification dispatcher.
- **Audit Persistence**: Every decision, bill submission, settlement, and override must dispatch an audit event via the repository.
- **Transaction Boundaries**: Ensure atomic commits across domain entity updates and audit records.
- **Decimals in DTOs**: Ensure all service method parameters and return values preserve `decimal.Decimal` types.
