# Feature Specification: Network Hospital & Coverage Administration
**Feature**: Network Hospital & Policy Product Administration  
**Target Acceptance Criteria**: AC-01, Network Governance  
**Specification File**: `specs/network_admin_spec.md`  
**Version**: 1.0.0  

---

## 1. Purpose
Defines the management, onboarding, tiering, and status activation of network hospitals, as well as the administration of versioned health insurance products, diagnostic rule-sets, auto-approval thresholds, and coverage rules.

---

## 2. Actors
- **Insurer Administrator**: Onboards hospitals, updates network active status, configures policy products and coverage limits.
- **Network Hospital**: Consumes network status to validate cashless authorization.
- **Customer**: Browses authorized network hospitals.

---

## 3. Inputs
- Hospital Onboarding: `hospital_id`, `hospital_name`, `tier` (`TIER_1` | `TIER_2` | `TIER_3`), `city`, `state`, `active_status` (boolean).
- Policy Configuration: `policy_code`, `product_name`, `default_sum_insured`, `auto_approval_threshold`, `buffer_percentage`, `auto_approved_diagnoses`, `exclusions`.

---

## 4. Outputs
- Hospital Directory Listing: Array of active network hospitals with tier and geographical location.
- Policy Rule Version Record: Immutable policy definition with version tag (e.g. `v1.2.0`).

---

## 5. Domain Rules
1. **Rule NET-01 (Active Status Gate)**: Only hospitals with `active_status == True` are recognized by the eligibility resolver. Suspended or un-onboarded hospitals are classified as `HOSP_OUT_OF_NETWORK`.
2. **Rule NET-02 (Policy Rule Immutability)**: Once a policy rule version is published, historical claims referencing that version remain bound to that version's rules even if new policy versions are published (**NFR-05**).

---

## 6. Error Handling
- `400 Bad Request`: Invalid hospital payload or negative auto-approval threshold.
- `409 Conflict`: Duplicate `hospital_id` or duplicate policy code.

---

## 7. Security Rules
- Only actors with role `ADMIN` can add or modify hospital network records or policy rules.

---

## 8. Audit Requirements
- All hospital additions, suspensions, and policy rule modifications are logged to `audit_logs` with admin identity and timestamp.

---

## 9. Acceptance Criteria
- **AC-NET-01**: Admin can onboard a new network hospital and toggle active status.
- **AC-NET-02**: Admin can configure auto-approval thresholds and diagnostic whitelists for a policy product.
- **AC-NET-03**: Network hospital directory is queryable by city and tier.
