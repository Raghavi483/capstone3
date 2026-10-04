# CLAUDE.md — Controller Layer Directives (`src/controllers/`)

## 1. Authentication & Role Boundaries (NFR-04)
- Enforce role boundaries on all endpoints: `CUSTOMER`, `HOSPITAL`, `INSURER`, `ADMIN`.
- **Hospital Tenancy Isolation**: Network hospitals may only access cases initiated at their facility (`hospital_id` claim matching resource `hospital_id`).
- **Admin Endpoints**: Elevated operations (such as override under AC-10 or network administration) require `ADMIN` role.

## 2. Request Handling & Logging (NFR-03, NFR-06)
- Validate request payloads using Pydantic models.
- Extract or generate `request_id` and `correlation_id` on every request.
- **ZERO PHI IN LOGS**: Never pass raw diagnostic codes or medical history to `logger.info()`. Log only `case_id`, `actor_id`, and `event`.
- Prohibit direct database access from controllers; all data access must route through services.
