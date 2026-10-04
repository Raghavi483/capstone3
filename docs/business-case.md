# Business Case Document: MediCard Cashless Hospitalization & Settlement Platform
**Document ID**: BC-AINE-017  
**Project**: MediCard  
**Domain**: Insurance — Health Cashless  
**Version**: 1.0.0  
**Status**: APPROVED  

---

## 1. Problem Statement

In conventional health insurance operations, cashless hospitalization is encumbered by high operational friction, fragmented communication across multiple stakeholders (policyholders, hospitals, third-party administrators, and insurers), and protracted pre-authorization turnaround times. Patients face anxiety at hospital admission desks when eligibility cannot be swiftly confirmed. Network hospitals risk non-payment or disputed claims due to ambiguous policy coverage, procedure exclusions, or unauthorized bill inflation. Insurers grapple with escalating loss ratios, settlement leakage, manual adjudication bottlenecks, and compliance vulnerabilities surrounding Protected Health Information (PHI).

The MediCard platform solves these challenges by providing a unified, multi-party digital orchestration platform that automates:
1. Instant real-time customer eligibility verification at hospital check-in.
2. Rule-driven pre-authorization decisioning with automatic approval for low-risk, standard diagnoses up to policy caps.
3. Transparent admission tracking and post-admission procedure updates.
4. Guaranteed settlement calculation enforcing strict mathematical caps (`pre_auth_amount + buffer`), co-pay, and deductible subtractions.
5. An immutable, append-only audit trail capturing every decision, state change, bill submission, and administrator override.

---

## 2. Target Users & Stakeholders

| Stakeholder Role | Description & Primary Objectives |
| :--- | :--- |
| **Customer / Policyholder** | Individuals covered under an active MediCard health policy. Requires instant coverage visibility (sum insured, remaining balance, exclusions, network hospital list), real-time status notifications, and transparent post-discharge settlement breakdowns. |
| **Network Hospital Desk / Billing** | Authorized hospital administration personnel who verify patient eligibility via `member_id` and `policy_id`, submit pre-authorization requests, record admissions, submit procedures and final bills, and track claim payouts. |
| **Insurer / Adjudicator** | Medical and claims adjudication officers reviewing complex or high-value pre-authorizations, raising queries for missing clinical documentation, and issuing partial or full approvals with policy reason codes. |
| **Insurer Administrator** | Senior governance officers possessing elevated override authority for auto-rejected pre-authorizations or escalated queries, maintaining network hospital rosters, and configuring versioned policy rules. |
| **Audit & Compliance Officer** | Internal/external auditors validating regulatory adherence, ensuring append-only ledger integrity, reviewing override justifications, and verifying zero PHI exposure in logs. |

---

## 3. Business Value & Value Proposition

- **Turnaround Time (TAT) Reduction**: Slashes pre-authorization approval time from hours/days to sub-second automated decisions for standard clinical pathways.
- **Leakage Prevention**: Enforces algorithmic caps preventing final bills from exceeding authorized pre-authorization thresholds plus configured buffer percentages.
- **Operational Efficiency**: Eliminates redundant manual phone calls and paperwork between hospital desks and claims desks via unified event tracking.
- **Audit Defensibility & Compliance**: Establishes an immutable, tamper-evident record of all claim transitions and administrative overrides while guaranteeing PHI privacy.
- **Customer Trust & Satisfaction**: Provides end-to-end transparency into claim progress and precise financial breakdowns of out-of-pocket expenses (co-pays and deductibles).

---

## 4. Success Metrics & Key Performance Indicators (KPIs)

| Metric | Target Objective | Measurement Mechanism |
| :--- | :--- | :--- |
| **Pre-Auth Auto-Approval Rate** | ≥ 60% for eligible standard diagnoses | Pre-auth engine telemetry |
| **Eligibility Verification Latency** | < 200 ms response time | API latency monitoring |
| **Settlement Calculation Accuracy** | 100% adherence to invariant formula | Automated invariant test suites |
| **Zero PHI Leakage** | 0 occurrences of diagnosis/procedure in plaintext logs | Automated static and dynamic log scan |
| **Audit Trail Completeness** | 100% of transitions and overrides logged with actor/timestamp | Append-only database ledger audit |
| **Health Check SLA** | HTTP 200 within 1 second of boot | Synthetic health endpoint monitor |

---

## 5. Domain Rules & Business Invariants

### 5.1 Eligibility Rules (AC-01, AC-02)
- A customer must have an active, non-expired policy linked to their account.
- The hospital where the patient seeks cashless admission must exist in the insurer's active network hospital directory.
- If policy is active and hospital is in-network, system returns `ELIGIBLE`. If inactive, expired, exhausted sum insured, or out-of-network, system returns `NOT_ELIGIBLE` accompanied by specific standardized reason codes (e.g., `POL_INACTIVE`, `HOSP_OUT_OF_NETWORK`, `SUM_INSURED_EXHAUSTED`).

### 5.2 Pre-Authorization & Auto-Approval Rules (AC-03, AC-04, AC-05)
- Every pre-authorization submission requires: `member_id`, `policy_id`, `hospital_id`, `admission_diagnosis`, `estimated_cost`, and `expected_admission_date`.
- Initial state is strictly `PENDING`.
- **Auto-Approval Rule**: IF `estimated_cost <= configured_threshold` AND `admission_diagnosis` is listed in the versioned policy's `auto_approved_diagnoses` list, THEN pre-auth is automatically approved up to the applicable policy cap.
- Non-qualifying requests transition to `QUERY_RAISED` (if documentation is incomplete) or remain in `PENDING` for adjudicator review, subsequently transitioning to `APPROVED`, `PARTIALLY_APPROVED`, or `REJECTED` with policy reason codes.

### 5.3 Admission & Claim Lifecycle Rules (AC-06, AC-08)
- A cashless claim strictly adheres to the state machine:
  `PRE_AUTH → ADMITTED → DISCHARGED → SETTLED` or `DISPUTED → CLOSED`.
- Any out-of-order transition (e.g., attempting to settle before discharge, or admitting without approved pre-auth) raises `InvalidClaimStateException`.

### 5.4 Settlement Formula & Mathematical Invariant (AC-07, NFR-01)
- The final bill submitted by the hospital must not exceed the pre-authorized amount plus the configured buffer percentage:
  $$\text{bill\_cap} = \text{pre\_auth\_amount} \times (1 + \text{buffer\_percentage})$$
  $$\text{effective\_bill} = \min(\text{final\_bill}, \text{bill\_cap})$$
- The final insurer settlement payout to the hospital is calculated as:
  $$\text{settlement\_amount} = \max(0, \text{effective\_bill} - \text{deductible} - \text{co\_pay})$$
- **Mandatory Invariant**: $\text{settlement\_amount} \ge 0$.
- All arithmetic MUST use fixed-point decimal (`Decimal`), never IEEE-754 floating-point numbers.

### 5.5 Insurer Override Governance (AC-10, NFR-02)
- An insurer administrator possesses the authority to override an auto-rejected pre-authorization or resolve an escalated query.
- Every override operation demands: `actor_id`, `timestamp`, `justification_reason`, and `authorized_amount`.
- Overrides are strictly append-only in the audit ledger and cannot overwrite prior decisions.

---

## 6. End-to-End User Journeys

### Journey 1: Customer Self-Service & Coverage Visibility
1. Customer registers in the portal and links their insurance policy.
2. Customer views policy coverage: total sum insured, remaining balance, policy exclusions, and network hospital directory.
3. During hospitalization, customer views real-time status transitions on a chronological case timeline.
4. Following discharge, customer inspects the itemized settlement summary showing total bill, insurer payout, co-pay, and deductible.

### Journey 2: Hospital Cashless Intake, Admission & Billing
1. Patient arrives at hospital desk; hospital staff performs eligibility check using `member_id` and `policy_id`.
2. Hospital receives `ELIGIBLE` status with coverage limits.
3. Hospital desk submits pre-authorization request with estimated costs and clinical diagnosis.
4. Upon approval, hospital records patient admission.
5. Post-treatment, hospital records procedure details and submits final itemized bill within buffer limits.
6. Hospital tracks settlement disbursement status.

### Journey 3: Adjudicator Review & Administrator Override
1. Adjudicator views pending pre-authorization queue for non-auto-approved cases.
2. Adjudicator evaluates clinical estimate against policy terms, approving or raising queries.
3. If an edge case requires policy exception, an Insurer Admin executes an override, supplying mandatory business justification.
4. Platform records immutable audit trail and notifies customer and hospital.

---

## 7. Functional Scope & Module Breakdown

1. **Member & Policy Management**: Customer registration, policy linking, policy rule versioning.
2. **Network Hospital Administration**: Onboarding, status toggling, and network tiering.
3. **Eligibility Verification Engine**: Multi-parameter real-time lookup with standardized failure reason codes.
4. **Pre-Authorization Decisioning Engine**: Automated rule-evaluator, policy cap validation, and query workflow.
5. **Adjudication Workbench**: Manual review queues, approval/rejection issuance, and administrator override.
6. **Admission & Procedure Tracker**: Hospital intake tracking, procedure recording, and discharge status updates.
7. **Settlement Calculator**: Fixed-point decimal arithmetic, buffer cap enforcement, co-pay/deductible resolution, and stubbed payout dispatch.
8. **Claim State Machine**: Rigid transition validation raising `InvalidClaimStateException` on violation.
9. **Audit & Timeline Ledger**: Append-only event store capturing actor, timestamp, action, and correlation IDs.
10. **Notification Dispatcher**: Stubbed multi-party notification service updating case timelines.
11. **Reports & Analytics**: Turnaround time (TAT), settlement volume, hospital query frequency, and loss ratio analytics.

---

## 8. Out-of-Scope Declarations (Brief Section 6.3)

To ensure rapid delivery, architectural discipline, and eliminate non-essential complexity, the following are explicitly out of scope:
- Real-time Hospital Information System (HIS) or Electronic Medical Record (EMR/EHR) integrations.
- Production banking / ACH / payment gateway rails (disbursement triggers are stubbed).
- Full international ICD-10 coding catalogs (a synthetic, domain-representative subset is utilized).
- Multi-currency or cross-border insurance policies.
- Advanced machine learning fraud detection models or real-time anomaly neural networks.
- Multi-region cloud infrastructure or enterprise hardware security modules (HSM).

---

## 9. Assumptions & Constraints

1. **Synthetic Data Exclusivity**: In strict compliance with Rule 4, all policyholders, member IDs, hospital names, diagnoses, and monetary figures are synthetically generated.
2. **Single-Command Local Execution**: The complete backend, frontend, and database run locally with zero external cloud dependencies.
3. **Fixed-Point Precision**: Currency is modeled with two decimal places using Python `Decimal`.
4. **Role Isolation**: Controller endpoints enforce authentication boundaries separating Customer, Hospital, Insurer, and Admin actors.
