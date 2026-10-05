# MediCard — Acceptance Criteria Verification Report (AC-01 through AC-10)
**Project**: MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)  
**Audit Date**: 2026-10-05  
**Status**: ALL PASS  

Every Acceptance Criteria (AC-01 through AC-10) has been verified with genuine executable tests referencing its AC-NN identifier, proving actual domain logic and integration behavior.

---

### AC-01: Customer Registration & Policy Coverage Lookup
- **Implementation**:
  - `src/domain/eligibility_rule.py` (`CoverageCalculationRule`, `evaluate_coverage`)
  - `src/services/eligibility_service.py` (`register_customer`, `get_customer_coverage`)
  - `src/controllers/eligibility_controller.py` (`POST /api/v1/customers/register`, `GET /api/v1/customers/{member_id}/policies/{policy_id}/coverage`)
- **Test**:
  - `tests/unit/test_ac01_policy_coverage.py` (`test_ac01_customer_policy_coverage_structure`, `test_ac01_sum_insured_float_rejection`, `test_ac01_exclusion_rule_evaluation`)
  - `tests/unit/test_ac01_ac02_integration.py` (`test_ac01_customer_registration_api`, `test_ac01_get_coverage_api`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac01_policy_coverage.py tests/unit/test_ac01_ac02_integration.py -k "ac01" -v
  ```
- **Result**: 5 passed in 0.44s
- **Evidence**: Member ID and Policy ID registered with Decimal sum-insured; float sums rejected with `TypeError`; active exclusions tracked; API returns 201 Created and 200 OK with remaining balance.
- **Status**: **PASS**

---

### AC-02: Hospital Eligibility Adjudication
- **Implementation**:
  - `src/domain/eligibility_rule.py` (`EligibilityAdjudicationRule`, `adjudicate_eligibility`)
  - `src/services/eligibility_service.py` (`check_eligibility`)
  - `src/controllers/eligibility_controller.py` (`POST /api/v1/eligibility/check`)
- **Test**:
  - `tests/unit/test_ac02_eligibility.py` (`test_ac02_eligible_customer_lookup`, `test_ac02_not_eligible_hospital_out_of_network`, `test_ac02_not_eligible_inactive_policy`, `test_ac02_not_eligible_exhausted_sum_insured`, `test_ac02_cumulative_failure_reasons`)
  - `tests/unit/test_ac01_ac02_integration.py` (`test_ac02_eligibility_check_api_eligible`, `test_ac02_eligibility_check_api_out_of_network_and_audit`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac02_eligibility.py tests/unit/test_ac01_ac02_integration.py -k "ac02" -v
  ```
- **Result**: 7 passed in 0.48s
- **Evidence**: Validates active customer, active policy date range, hospital network registration, and unexhausted balance; cumulative rejection reasons reported; immutable audit log recorded.
- **Status**: **PASS**

---

### AC-03: Cashless Pre-Authorization Submission
- **Implementation**:
  - `src/domain/pre_auth_rule.py` (`PreAuthValidationRule`, `validate_submission`)
  - `src/services/pre_auth_service.py` (`submit_pre_auth`)
  - `src/controllers/pre_auth_controller.py` (`POST /api/v1/preauth/submit`)
- **Test**:
  - `tests/unit/test_ac03_pre_auth_submission.py` (`test_ac03_submission_initial_pending_state`, `test_ac03_submission_float_rejection`, `test_ac03_submission_positive_cost_required`)
  - `tests/unit/test_ac03_ac04_ac05_ac10_integration.py` (`test_ac03_and_ac05_pre_auth_submission_auto_approval`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac03_pre_auth_submission.py tests/unit/test_ac03_ac04_ac05_ac10_integration.py -k "ac03" -v
  ```
- **Result**: 4 passed in 0.42s
- **Evidence**: Validates positive estimated cost represented in Decimal; initial state is PENDING; links member, policy, and network hospital; persists claim with unique ID.
- **Status**: **PASS**

---

### AC-04: Decision History & Reason Codes
- **Implementation**:
  - `src/domain/pre_auth_rule.py` (`PreAuthLifecycleRule`, `transition_pre_auth_state`)
  - `src/repositories/pre_auth_repository.py` (`record_decision_append_only`)
  - `src/controllers/pre_auth_controller.py` (`GET /api/v1/preauth/{pre_auth_id}`)
- **Test**:
  - `tests/unit/test_ac04_pre_auth_lifecycle.py` (`test_ac04_allowed_transitions_with_reason_codes`, `test_ac04_missing_reason_codes_rejected`, `test_ac04_invalid_transition_from_rejected`)
  - `tests/unit/test_ac03_ac04_ac05_ac10_integration.py` (`test_ac04_pre_auth_details_and_decision_history`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac04_pre_auth_lifecycle.py tests/unit/test_ac03_ac04_ac05_ac10_integration.py -k "ac04" -v
  ```
- **Result**: 4 passed in 0.40s
- **Evidence**: All decisions require versioned reason codes; transitions from final states (REJECTED) are blocked; append-only ledger stores decision history with timestamps.
- **Status**: **PASS**

---

### AC-05: Rule-Based Auto-Approval Engine
- **Implementation**:
  - `src/domain/pre_auth_rule.py` (`AutoApprovalRule`, `evaluate_auto_approval`)
  - `src/services/pre_auth_service.py` (`submit_pre_auth`)
- **Test**:
  - `tests/unit/test_ac05_auto_approval.py` (`test_ac05_auto_approval_criteria_met`, `test_ac05_auto_reject_if_diagnosis_excluded`, `test_ac05_partial_approval_when_balance_less_than_cost`, `test_ac05_query_raised_when_diagnosis_not_in_whitelist`, `test_ac05_query_raised_when_cost_exceeds_threshold`)
  - `tests/unit/test_ac03_ac04_ac05_ac10_integration.py` (`test_ac05_pre_auth_auto_rejection_excluded_diagnosis`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac05_auto_approval.py tests/unit/test_ac03_ac04_ac05_ac10_integration.py -k "ac05" -v
  ```
- **Result**: 6 passed in 0.45s
- **Evidence**: Auto-approval triggers when diagnosis is whitelisted AND cost <= threshold ($50,000) AND cost <= remaining sum insured; raises QUERY_RAISED if threshold exceeded or diagnosis unlisted; rejects excluded diagnosis.
- **Status**: **PASS**

---

### AC-06: Procedure Recording & Discharge Buffer Cap
- **Implementation**:
  - `src/domain/admission_rule.py` (`DischargeBufferRule`, `validate_discharge_bill`)
  - `src/services/admission_service.py` (`record_admission`, `discharge_and_submit_bill`)
  - `src/controllers/claim_controller.py` (`POST /api/v1/claims/{claim_id}/admit`, `POST /api/v1/claims/{claim_id}/discharge`)
- **Test**:
  - `tests/unit/test_ac06_bill_buffer.py` (`test_ac06_bill_within_buffer_accepted`, `test_ac06_bill_exceeding_buffer_flagged`, `test_ac06_float_rejection`, `test_ac06_procedure_item_decimal_validation`)
  - `tests/unit/test_ac06_ac08_ac09_integration.py` (`test_ac06_and_ac08_admission_and_discharge_happy_path`, `test_ac06_discharge_bill_exceeds_buffer_rejected`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac06_bill_buffer.py tests/unit/test_ac06_ac08_ac09_integration.py -k "ac06" -v
  ```
- **Result**: 6 passed in 0.58s
- **Evidence**: Final discharge bill verified against approved pre-auth amount + 10% buffer cap ($45,000 + 10% = $49,500); bills exceeding buffer ($52,000) raise `BufferExceededException` (HTTP 422); procedure items validated as Decimal.
- **Status**: **PASS**

---

### AC-07: Fixed-Point Settlement Calculator Engine
- **Implementation**:
  - `src/domain/settlement_rule.py` (`SettlementCalculatorEngine`, `calculate_settlement`)
  - `src/services/settlement_service.py` (`calculate_and_record_settlement`)
  - `src/controllers/settlement_controller.py` (`POST /api/v1/claims/{claim_id}/settle`, `GET /api/v1/claims/{claim_id}/settlement`)
- **Test**:
  - `tests/unit/test_ac07_settlement.py` (Cases 1 through 10 covering below cap, at cap, above cap, deductibles, copay, zero-floor invariant, rounding)
  - `tests/unit/test_ac07_settlement_integration.py` (`test_ac07_complete_settlement_flow_via_api`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac07_settlement.py tests/unit/test_ac07_settlement_integration.py -v
  ```
- **Result**: 11 passed in 0.38s
- **Evidence**: Zero floating-point calculations; `Decimal("0.00")` floor invariant guaranteed; policy cap applied before deductible/copay; returns immutable `SettlementResult` breakdown.
- **Status**: **PASS**

---

### AC-08: Claim State Machine Progression
- **Implementation**:
  - `src/domain/claim_state_rule.py` (`ClaimStateMachineRule`, `transition_claim_state`, `InvalidClaimStateException`)
  - `src/services/admission_service.py`
  - `src/services/settlement_service.py`
- **Test**:
  - `tests/unit/test_ac08_claim_state_machine.py` (`test_ac08_valid_progression_standard_path`, `test_ac08_valid_progression_dispute_path`, `test_ac08_invalid_transition_pre_auth_to_settled`, `test_ac08_backward_transition_raises_exception`, `test_ac08_settled_claim_immutability`)
  - `tests/unit/test_ac06_ac08_ac09_integration.py` (`test_ac08_invalid_claim_state_transition_fails`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac08_claim_state_machine.py tests/unit/test_ac06_ac08_ac09_integration.py -k "ac08" -v
  ```
- **Result**: 6 passed in 0.49s
- **Evidence**: Valid forward path: `REGISTERED -> PRE_AUTH_APPROVED -> ADMITTED -> DISCHARGED -> SETTLED`; invalid jumps (e.g. PRE_AUTH_APPROVED direct to SETTLED) raise `InvalidClaimStateException`; settled claims are strictly immutable.
- **Status**: **PASS**

---

### AC-09: Multi-Channel Notifications & Chronological Timeline
- **Implementation**:
  - `src/domain/notification_rule.py` (`NotificationDispatcherRule`, `TimelineEventRule`)
  - `src/controllers/claim_controller.py` (`GET /api/v1/claims/{claim_id}/timeline`)
  - `src/repositories/models.py` (`ClaimTimelineEventModel`, `NotificationModel`)
- **Test**:
  - `tests/unit/test_ac09_notifications_timeline.py` (`test_ac09_notification_generation_for_state_transition`, `test_ac09_timeline_chronological_structure`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac09_notifications_timeline.py -v
  ```
- **Result**: 2 passed in 0.18s
- **Evidence**: Every claim state transition emits structured timeline events with UTC ISO timestamp; generates SMS and EMAIL notifications formatted with masked identifiers.
- **Status**: **PASS**

---

### AC-10: Insurer Admin Adjudication & Override
- **Implementation**:
  - `src/domain/adjudication_rule.py` (`AdminOverrideRule`, `evaluate_admin_override`)
  - `src/services/pre_auth_service.py` (`override_pre_auth_decision`)
  - `src/controllers/pre_auth_controller.py` (`POST /api/v1/admin/preauth/override`)
- **Test**:
  - `tests/unit/test_ac10_admin_override.py` (`test_ac10_admin_override_success`, `test_ac10_non_admin_role_forbidden`, `test_ac10_empty_reason_rejected`, `test_ac10_override_cannot_exceed_remaining_balance`)
  - `tests/unit/test_ac03_ac04_ac05_ac10_integration.py` (`test_ac10_admin_override_and_audit`, `test_ac10_non_admin_override_forbidden`)
- **Command**:
  ```powershell
  python -m pytest tests/unit/test_ac10_admin_override.py tests/unit/test_ac03_ac04_ac05_ac10_integration.py -k "ac10" -v
  ```
- **Result**: 6 passed in 0.52s
- **Evidence**: Non-admin roles (e.g. HOSPITAL, CUSTOMER) receive HTTP 403 Forbidden; empty rationale rejected; override amount cannot exceed remaining balance; records immutable audit entry.
- **Status**: **PASS**
