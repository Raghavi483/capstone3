# CLAUDE.md — Frontend Directives (`frontend/`)

## 1. Multi-Party Persona Requirements
The user interface must provide distinct, accessible portals for all 4 system personas:
1. **Customer View**: Member registration, policy details, coverage (sum insured, remaining balance, exclusions, network hospitals), real-time claim timeline, post-discharge settlement summary.
2. **Hospital View**: Member eligibility lookup, pre-auth submission form, patient admission tracker, procedure and final bill submission.
3. **Insurer / Adjudicator View**: Pending pre-auth queue, query workflow, approval / rejection actions, admin override panel with mandatory justification.
4. **Admin View**: Network hospital management, policy rules administration, audit inspection, and operational analytics.

## 2. Technical & Testing Constraints
- Responsive layout supporting both desktop and mobile viewports.
- All interactive elements must have unique, deterministic `id` or `data-testid` attributes to support Playwright automated E2E testing.
- Visual polish is secondary to functional completeness, state machine feedback, and Playwright testability.
